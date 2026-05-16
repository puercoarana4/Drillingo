"use client";

import { useState, useRef } from "react";
import YouTube, { YouTubeEvent, YouTubePlayer } from "react-youtube";

interface DrillYoutubePlayerProps {
  videoId: string;
  title?: string;
  onFirstPlay?: () => void;
  onError?: () => void;
}

export default function DrillYoutubePlayer({
  videoId,
  title,
  onFirstPlay,
  onError,
}: DrillYoutubePlayerProps) {
  const [ready, setReady] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [hasPlayed, setHasPlayed] = useState(false);
  const [embedError, setEmbedError] = useState(false);
  const playerRef = useRef<YouTubePlayer | null>(null);

  const opts = {
    width: "100%",
    height: "100%",
    playerVars: {
      autoplay: 0,
      modestbranding: 1,
      rel: 0,
      color: "white",
    },
  };

  function handleReady(e: YouTubeEvent) {
    playerRef.current = e.target;
    setReady(true);
  }

  function handlePlay() {
    setPlaying(true);
    if (!hasPlayed) {
      setHasPlayed(true);
      onFirstPlay?.();
    }
  }

  function handlePause() {
    setPlaying(false);
  }

  function handleError() {
    setEmbedError(true);
    onError?.();
  }

  // Fallback when YouTube blocks the embed
  if (embedError) {
    return (
      <div className="rounded-xl border border-border bg-surface p-4 text-center">
        <p className="text-muted text-sm mb-2">
          🔒 This video cannot be embedded.
        </p>
        <a
          href={`https://www.youtube.com/watch?v=${videoId}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent text-sm hover:underline font-display uppercase tracking-wider"
        >
          Watch on YouTube →
        </a>
        <p className="text-muted text-xs mt-2">
          Open the video, listen to the bar, then fill in the blanks below.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl overflow-hidden border border-border bg-black">
      {title && (
        <div className="px-4 py-2 bg-surface border-b border-border flex items-center gap-2">
          <span className="text-accent text-xs">▶</span>
          <p className="font-display text-xs uppercase tracking-wider text-muted truncate">
            {title}
          </p>
          {playing && (
            <span className="ml-auto flex gap-0.5">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="w-0.5 bg-accent rounded-full animate-pulse"
                  style={{
                    height: `${8 + i * 4}px`,
                    animationDelay: `${i * 0.15}s`,
                  }}
                />
              ))}
            </span>
          )}
        </div>
      )}
      <div className="relative w-full" style={{ paddingBottom: "56.25%" }}>
        <div className="absolute inset-0">
          <YouTube
            videoId={videoId}
            opts={opts}
            onReady={handleReady}
            onPlay={handlePlay}
            onPause={handlePause}
            onError={handleError}
            className="w-full h-full"
            iframeClassName="w-full h-full"
          />
        </div>
      </div>
    </div>
  );
}
