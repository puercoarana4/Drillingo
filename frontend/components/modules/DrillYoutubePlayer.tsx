"use client";

import { useState, useRef } from "react";
import YouTube, { YouTubeEvent, YouTubePlayer } from "react-youtube";

interface DrillYoutubePlayerProps {
  videoId: string;
  title?: string;
  /** Called when the video starts playing for the first time */
  onFirstPlay?: () => void;
}

export default function DrillYoutubePlayer({
  videoId,
  title,
  onFirstPlay,
}: DrillYoutubePlayerProps) {
  const [ready, setReady] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [hasPlayed, setHasPlayed] = useState(false);
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
            className="w-full h-full"
            iframeClassName="w-full h-full"
          />
        </div>
      </div>
      {!ready && (
        <div className="absolute inset-0 flex items-center justify-center bg-black">
          <div className="animate-spin h-8 w-8 border-2 border-accent border-t-transparent rounded-full" />
        </div>
      )}
    </div>
  );
}
