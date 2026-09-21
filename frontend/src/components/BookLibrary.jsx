import { useState, useMemo, useEffect } from 'react'
import BookCard from './BookCard'
import { fetchBooks } from '../api/books'


function BookLibrary() {
  const [ageFilter, setAgeFilter] = useState('All ages')
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchBooks()
      .then((data) => setBooks(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const filteredBooks = useMemo(() => {
    if (ageFilter === 'All ages') return books
    return books.filter((book) => book.age_group === ageFilter)
  }, [books, ageFilter])

  const ageGroups = useMemo(() => {
    const unique = [...new Set(books.map((book) => book.age_group))]
    return ['All ages', ...unique.sort()]
  }, [books])

  return (
    <section id="library" className="bg-paper py-16">
      <div className="max-w-6xl mx-auto px-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-10">
          <div>
            <h2 className="font-display text-3xl font-bold text-ink">Our Library</h2>
            <p className="font-body text-ink/70 mt-1">Books matched to your child&apos;s reading level</p>
          </div>

          <div className="flex items-center gap-3 sm:ml-auto">
            <label htmlFor="age-sort" className="font-body text-sm text-ink/70 whitespace-nowrap">
              Sort by age:
            </label>
            <select
              id="age-sort"
              value={ageFilter}
              onChange={(e) => setAgeFilter(e.target.value)}
              className="font-body text-sm border border-paper-soft bg-paper-soft text-ink rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer"
            >
              {ageGroups.map((age) => (
                <option key={age} value={age}>{age}</option>
              ))}
            </select>
          </div>
        </div>

        {loading && <p className="font-body text-center text-ink/60 py-12">Loading books…</p>}
        {error && <p className="font-body text-center text-red-700 py-12">{error}</p>}

        {!loading && !error && (
          filteredBooks.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {filteredBooks.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
          ) : (
            <p className="font-body text-center text-ink/60 py-12">No books found for this age group.</p>
          )
        )}
      </div>
    </section>
  )

}
export default BookLibrary