import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchBook } from '../api/books'

function BookPage() {
  const { id } = useParams()
  const [book, setBook] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    fetchBook(id)
      .then((data) => {
        if (!cancelled) setBook(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [id])

  return (
    <main className="max-w-3xl mx-auto px-4 py-10">
      <Link to="/" className="font-body text-sm text-primary hover:underline">
        ← Back to library
      </Link>

      {loading && <p className="mt-6 font-body text-ink/60">Loading…</p>}
      {error && <p className="mt-6 font-body text-red-600">{error}</p>}

      {book && (
        <article className="mt-6">
          <h1 className="font-display text-3xl font-semibold text-ink mb-3">
            {book.title}
          </h1>
          <span className="inline-block bg-primary/10 text-primary font-body text-sm font-medium px-3 py-1 rounded-full">
            Ages {book.age_group}
          </span>

          {book.text ? (
            <p className="mt-6 font-body text-lg leading-8 text-ink whitespace-pre-wrap">
              {book.text}
            </p>
          ) : (
            <p className="mt-6 font-body text-ink/60">Text coming soon.</p>
          )}
        </article>
      )}
    </main>
  )
}

export default BookPage
