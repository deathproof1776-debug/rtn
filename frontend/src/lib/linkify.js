/**
 * linkifyText - Converts plain-text URLs into clickable <a> elements.
 * Handles https://, http://, and www. prefixed links.
 * Returns an array suitable for rendering inside a React element.
 */
export function linkifyText(text) {
  if (!text) return null;
  // Match http(s):// URLs OR www. prefixed domains
  const urlRegex = /(https?:\/\/[^\s]+|www\.[^\s]+\.[^\s]+)/g;
  const parts = text.split(urlRegex);
  return parts.map((part, i) => {
    if (/^https?:\/\//.test(part) || /^www\./i.test(part)) {
      const href = /^https?:\/\//.test(part) ? part : `https://${part}`;
      return (
        <a
          key={i}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[var(--brand-primary)] underline hover:opacity-80 break-all"
          onClick={(e) => e.stopPropagation()}
        >
          {part}
        </a>
      );
    }
    return part;
  });
}
