name: Preview thumbnails (no email)

on:
  workflow_dispatch: {}

jobs:
  build-only:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install fonts and dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y fonts-poppins fonts-inter || true
          pip install -r requirements.txt

      - name: Generate images
        run: python generate.py

      - name: Upload for preview
        uses: actions/upload-artifact@v4
        with:
          name: preview
          path: output/*.jpg
