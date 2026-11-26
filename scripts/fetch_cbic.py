import base64
import csv
import hashlib
import ssl
import time
from pathlib import Path

import httpx
import truststore
from protego import Protego

from gstsaathi.ingest.fetch import USER_AGENT, Manifest, now_iso, slug

API = "https://taxinformation.cbic.gov.in/api/cbic-circular-msts"
LIST_URL = f"{API}/fetchAllCircularsByTaxId/1000001"
DOWNLOAD_URL = f"{API}/download"
RAW = Path("data/raw/cbic")
SOURCES = Path("data/sources.csv")
MANIFEST_PATH = Path("data/manifest.jsonl")
LICENCE = (
    "CBIC Copyright Policy: free reproduction with accurate use "
    "and source acknowledgement; third-party content excluded"
)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = Manifest(MANIFEST_PATH)

    context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    headers = {"User-Agent": USER_AGENT}

    with httpx.Client(
        headers=headers,
        timeout=90,
        verify=context,
        follow_redirects=True,
    ) as client:
        robots_response = client.get("https://taxinformation.cbic.gov.in/robots.txt")
        robots_response.raise_for_status()
        robots = Protego.parse(robots_response.text)

        response = client.get(LIST_URL)
        response.raise_for_status()
        records = response.json()

        active = [item for item in records if str(item.get("isActive", "")).upper() == "Y"]

        existing = set()
        if SOURCES.exists():
            with SOURCES.open(encoding="utf-8", newline="") as file:
                existing = {row["url"] for row in csv.DictReader(file)}

        new_rows = []
        for item in active:
            url = f"{DOWNLOAD_URL}/{item['id']}/ENG"
            title = (
                f"{item.get('circularNo', 'Circular')} — {item.get('circularName', '')}"
            ).strip(" —")
            if url not in existing:
                new_rows.append(
                    {
                        "url": url,
                        "source": "cbic",
                        "licence": LICENCE,
                        "title": title,
                    }
                )
                existing.add(url)

        if new_rows:
            with SOURCES.open("a", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["url", "source", "licence", "title"],
                )
                writer.writerows(new_rows)

        print(f"Active API records: {len(active)}")
        print(f"New source entries: {len(new_rows)}")

        downloaded = 0
        skipped = 0
        failed = 0

        for index, item in enumerate(active, start=1):
            url = f"{DOWNLOAD_URL}/{item['id']}/ENG"
            title = (
                f"{item.get('circularNo', 'Circular')} — {item.get('circularName', '')}"
            ).strip(" —")

            if manifest.done(url, Path(".")):
                skipped += 1
                continue

            if not robots.can_fetch("examate-student-bot", url):
                print(f"BLOCKED: {item['id']}")
                failed += 1
                continue

            try:
                if index > 1:
                    time.sleep(0.5)

                result = client.get(url)
                result.raise_for_status()
                payload = result.json()
                pdf = base64.b64decode(payload["data"], validate=True)

                if not pdf.startswith(b"%PDF-"):
                    raise ValueError("Decoded response is not a PDF")

                filename = f"circular-{slug(item.get('circularNo') or 'circular')}-{item['id']}.pdf"
                target = RAW / filename
                temporary = target.with_suffix(".pdf.part")
                temporary.write_bytes(pdf)
                temporary.replace(target)

                manifest.add(
                    {
                        "url": url,
                        "source": "cbic",
                        "licence": LICENCE,
                        "title": title,
                        "via": "cbic-api",
                        "path": target.as_posix(),
                        "bytes": len(pdf),
                        "sha256": hashlib.sha256(pdf).hexdigest(),
                        "content_type": "application/pdf",
                        "http_status": result.status_code,
                        "status": "downloaded",
                        "attempts": 1,
                        "fetched_at": now_iso(),
                    }
                )
                downloaded += 1
                print(f"[{index}/{len(active)}] OK {title}")

            except Exception as error:
                failed += 1
                print(f"[{index}/{len(active)}] FAILED {item['id']}: {error}")

        print("\nCBIC download summary")
        print(f"Downloaded: {downloaded}")
        print(f"Already present: {skipped}")
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
