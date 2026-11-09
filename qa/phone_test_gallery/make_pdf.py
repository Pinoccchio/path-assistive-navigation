from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


GALLERY = Path(__file__).resolve().parent
OUTPUT = GALLERY / "phone_test_slideshow.pdf"
IMAGES = sorted(GALLERY.glob("[0-9][0-9]_*.jpg"))
PAGE_SIZE = (1920, 1080)


def make_page(path: Path) -> Image.Image:
    page = Image.new("RGB", PAGE_SIZE, "#101820")
    with Image.open(path) as source:
        picture = source.convert("RGB")
        picture.thumbnail((1840, 920), Image.Resampling.LANCZOS)
        x = (PAGE_SIZE[0] - picture.width) // 2
        y = (PAGE_SIZE[1] - picture.height) // 2 - 30
        page.paste(picture, (x, y))

    label = path.stem[3:].replace("_", " ").title()
    draw = ImageDraw.Draw(page)
    draw.text((48, 1010), f"{path.stem[:2]}  {label}", fill="white", font=ImageFont.load_default(size=36))
    return page


if __name__ == "__main__":
    if not IMAGES:
        raise SystemExit("No test images found")
    pages = [make_page(path) for path in IMAGES]
    pages[0].save(OUTPUT, "PDF", save_all=True, append_images=pages[1:], resolution=150)
    print(f"Created {OUTPUT} with {len(pages)} pages")
