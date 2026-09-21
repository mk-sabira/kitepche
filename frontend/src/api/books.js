const BOOKS_URL = 'http://localhost:8000/books'

export async function fetchBooks() {
    const response = await fetch(BOOKS_URL)
    
    if (!response.ok) {
        throw new Error('Could not load books. Please try again.')
    }

    return response.json()
}