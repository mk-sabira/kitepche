import { Link } from 'react-router-dom'

function Banner() {
  return (
    <section className="bg-paper-soft">
      <div className="max-w-6xl mx-auto px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="order-2 lg:order-1">
            <p className="text-highlight font-body font-semibold text-sm uppercase tracking-wide mb-3">
              Кыргыз тилинде окуу
            </p>
            <h1 className="font-display text-4xl lg:text-5xl font-bold text-ink leading-tight mb-6">
              Discover the joy of reading in Kyrgyz
            </h1>
            <p className="font-body text-lg text-ink/80 leading-relaxed mb-8 max-w-lg">
              Kitepche helps children find books matched to their reading level.
              Explore our library, track progress, and grow a love for Kyrgyz literature.
            </p>
            <div className="flex flex-wrap gap-4">
              <a
                href="/#library"
                className="bg-primary hover:bg-primary-dark text-white font-body font-medium px-6 py-3 rounded-full transition-colors"
              >
                Browse Library
              </a>
              <Link
                to="/analyze"
                className="border-2 border-primary text-primary hover:bg-primary hover:text-white font-body font-medium px-6 py-3 rounded-full transition-colors"
              >
                Analyze Text
              </Link>
            </div>
          </div>

          <div className="order-1 lg:order-2 flex justify-center">
            <div className="relative w-full max-w-md">
              <div className="absolute -inset-4 bg-primary/10 rounded-3xl -rotate-2" />
              <img
                src="/hero-child-book.jpg"
                alt="Child holding a book and reading"
                className="relative w-full rounded-2xl shadow-lg object-cover aspect-[4/5]"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Banner
