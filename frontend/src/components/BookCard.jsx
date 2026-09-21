function BookCard({ book }) {
  return (
    <article className="bg-paper rounded-2xl overflow-hidden shadow-sm border border-paper-soft hover:shadow-md transition-shadow">
      <div className="aspect-[3/4] overflow-hidden bg-paper-soft">
        <img
          src={book.cover_url}
          alt={book.title}
          className="w-full h-full object-cover"
          onError={(e) => {
            e.target.style.display = 'none'
            e.target.nextSibling.style.display = 'flex'
          }}
        />
        
      </div>
      <div className="p-4">
        <h3 className="font-display text-lg font-semibold text-ink mb-2 line-clamp-2">
          {book.title}
        </h3>
        <span className="inline-block bg-primary/10 text-primary font-body text-sm font-medium px-3 py-1 rounded-full">
          Ages {book.age_group}
        </span>
      </div>
    </article>
  )
}

export default BookCard
