type Props = {
  label: string;
  className?: string;
};

export function Annotation({ label, className = "" }: Props) {
  return (
    <p
      className={`max-w-[22rem] border-l border-brass-500/70 pl-2.5 text-[11px] leading-relaxed text-zinc-500 ${className}`}
    >
      {label}
    </p>
  );
}
