"use client";

import { useRef, useState, useEffect } from "react";

interface AudioPlayerProps {
  /** URL pointing directly to Object Storage (S3/Supabase) — never a BLOB (Req 5.7, 5.8) */
  audioUrl: string;
  title?: string;
}

const SPEEDS = [0.75, 1, 1.25] as const;
type Speed = (typeof SPEEDS)[number];

export default function AudioPlayer({ audioUrl, title }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speed, setSpeed] = useState<Speed>(1);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onTimeUpdate = () => {
      if (audio.duration) setProgress(audio.currentTime / audio.duration);
    };
    const onLoadedMetadata = () => setDuration(audio.duration);
    const onEnded = () => setPlaying(false);

    audio.addEventListener("timeupdate", onTimeUpdate);
    audio.addEventListener("loadedmetadata", onLoadedMetadata);
    audio.addEventListener("ended", onEnded);

    return () => {
      audio.removeEventListener("timeupdate", onTimeUpdate);
      audio.removeEventListener("loadedmetadata", onLoadedMetadata);
      audio.removeEventListener("ended", onEnded);
    };
  }, []);

  function togglePlay() {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
    } else {
      audio.play();
    }
    setPlaying(!playing);
  }

  function handleSeek(e: React.ChangeEvent<HTMLInputElement>) {
    const audio = audioRef.current;
    if (!audio || !audio.duration) return;
    const newTime = parseFloat(e.target.value) * audio.duration;
    audio.currentTime = newTime;
    setProgress(parseFloat(e.target.value));
  }

  function handleSpeedChange(s: Speed) {
    setSpeed(s);
    if (audioRef.current) audioRef.current.playbackRate = s;
  }

  function formatTime(seconds: number) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  return (
    // Req 5.8: client streams directly from Object Storage URL
    <div className="bg-surface border border-border rounded-xl p-4">
      <audio ref={audioRef} src={audioUrl} preload="metadata" />

      {title && (
        <p className="font-display text-sm uppercase tracking-wider text-muted mb-3 truncate">
          {title}
        </p>
      )}

      {/* Progress bar */}
      <div className="flex items-center gap-3 mb-3">
        <span className="text-xs text-muted w-10 text-right">
          {formatTime(progress * duration)}
        </span>
        <input
          type="range"
          min={0}
          max={1}
          step={0.001}
          value={progress}
          onChange={handleSeek}
          className="flex-1 h-1 accent-accent cursor-pointer"
          aria-label="Audio progress"
        />
        <span className="text-xs text-muted w-10">{formatTime(duration)}</span>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        {/* Play/Pause */}
        <button
          onClick={togglePlay}
          className="w-12 h-12 rounded-full bg-accent flex items-center justify-center hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-surface"
          aria-label={playing ? "Pause" : "Play"}
        >
          {playing ? (
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
          ) : (
            <svg className="w-5 h-5 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7L8 5z" />
            </svg>
          )}
        </button>

        {/* Speed selector */}
        <div className="flex gap-1">
          {SPEEDS.map((s) => (
            <button
              key={s}
              onClick={() => handleSpeedChange(s)}
              className={[
                "px-2 py-1 rounded text-xs font-display uppercase transition-colors",
                speed === s
                  ? "bg-accent text-white"
                  : "bg-border text-muted hover:text-foreground",
              ].join(" ")}
              aria-label={`Playback speed ${s}x`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
