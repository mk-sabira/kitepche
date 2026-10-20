import { API_URL } from './config'


const BOOKS_URL = `${API_URL}/books`


export async function fetchBooks() {
    const response = await fetch(BOOKS_URL)
    
    if (!response.ok) {
        throw new Error('Could not load books. Please try again.')
    }

    return response.json()
}



export async function fetchBook(id) {
    const response = await fetch(`${BOOKS_URL}/${id}`)

    if (response.status === 404) {
        const error = new Error('Book not found.')
        error.status = 404
        throw error
    }

    if (!response.ok) {
        throw new Error('Could not load the book. Please try again.')
    }

    return response.json()
}
