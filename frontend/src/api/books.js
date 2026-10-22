import { API_URL } from './config'
import { fetchWithRetry } from './fetchWithRetry'


const BOOKS_URL = `${API_URL}/books`


export async function fetchBooks(onRetry) {
    const response = await fetchWithRetry(BOOKS_URL, {}, { onRetry })
    
    if (!response.ok) {
        throw new Error('Could not load books. Please try again.')
    }

    return response.json()
}



export async function fetchBook(id, onRetry) {
    const response = await fetchWithRetry(`${BOOKS_URL}/${id}`, {}, { onRetry })

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
