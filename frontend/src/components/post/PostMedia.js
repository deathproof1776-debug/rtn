export default function PostMedia({ images, testId }) {
  if (!images?.length) return null;

  return (
    <div className="mb-3 md:mb-4 grid grid-cols-2 gap-1.5 md:gap-2" data-testid={testId}>
      {images.slice(0, 4).map((img, i) => (
        <img
          key={`img-${img.slice(-20)}-${i}`}
          src={img}
          alt={`Post image ${i + 1}`}
          className="w-full h-24 md:h-32 object-cover border border-[var(--border-color)]"
        />
      ))}
    </div>
  );
}
