import ReactMarkdown from 'react-markdown';

interface MarkdownContentProps {
  content: string;
  className?: string;
}

export function MarkdownContent({ content, className = '' }: MarkdownContentProps) {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        components={{
          h1: ({ children }) => <h1 className="text-lg font-bold text-white mb-2 mt-1">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-bold text-white mb-2 mt-3">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-semibold text-slate-200 mb-1 mt-2">{children}</h3>,
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
          em: ({ children }) => <em className="text-slate-400 italic">{children}</em>,
          ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-2 ml-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-2 ml-1">{children}</ol>,
          li: ({ children }) => <li className="text-slate-300">{children}</li>,
          code: ({ children }) => (
            <code className="px-1.5 py-0.5 rounded bg-slate-900 text-emerald-300 text-xs font-mono">{children}</code>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-emerald-500/50 pl-3 my-2 text-slate-400 italic">{children}</blockquote>
          ),
          hr: () => <hr className="border-slate-700 my-3" />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
