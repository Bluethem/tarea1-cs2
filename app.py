import requests
from bs4 import BeautifulSoup
from datetime import datetime


def analyze_url(url):
    response = requests.get(url, timeout=10)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string if soup.title else "Sin título"

    text = soup.get_text(separator=" ", strip=True)

    words = text.split()

    return {
        "url": url,
        "title": title,
        "characters": len(text),
        "words": len(words),
        "analyzed_at": datetime.now()
    }


def main():
    print("=== Security News Analyzer ===")

    url = input("Ingrese una URL: ")

    try:
        result = analyze_url(url)

        print("\nResultado")
        print("-" * 40)
        print(f"Título: {result['title']}")
        print(f"Caracteres: {result['characters']}")
        print(f"Palabras: {result['words']}")
        print(f"Fecha: {result['analyzed_at']}")

    except requests.exceptions.RequestException as error:
        print(f"Error al acceder a la URL: {error}")


if __name__ == "__main__":
    main()
