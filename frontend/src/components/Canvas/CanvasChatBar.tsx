import { useState, useRef, useEffect } from "react";
import { modifyCanvas, getCanvasModification } from "@/lib/api";
import { PlaceholdersAndVanishInput } from "@/components/ui/placeholders-and-vanish-input";

interface Props {
  campaignId: string;
  onUpdated?: () => void; // call to refetch canvas
}

export default function CanvasChatBar({ campaignId, onUpdated }: Props) {
  const [value, setValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingModId, setPendingModId] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  const pollStatus = (modId: string) => {
    let attempts = 0;
    pollRef.current = window.setInterval(async () => {
      attempts += 1;
      try {
        const res = await getCanvasModification(campaignId, modId);
        if (res.status === "completed") {
          window.clearInterval(pollRef.current!);
          setPendingModId(null);
          setLoading(false);
          onUpdated?.();
        }
      } catch (e: any) {
        console.error("Poll error", e);
        window.clearInterval(pollRef.current!);
        setLoading(false);
        setPendingModId(null);
      }
      if (attempts > 60) {
        window.clearInterval(pollRef.current!);
        setLoading(false);
        setPendingModId(null);
      }
    }, 3000);
  };

  const onSend = async () => {
    const msg = value.trim();
    if (!msg || loading) return;
    setLoading(true);
    try {
      const res = await modifyCanvas(campaignId, msg);
      if (res.status === "completed") {
        onUpdated?.();
        setLoading(false);
      } else {
        setPendingModId(res.modification_id);
        pollStatus(res.modification_id);
      }
      setValue("");
    } catch (e) {
      setLoading(false);
    }
  };

  const placeholders = [
    "change image of day 1",
    "change caption of day 2",
    "add total cost to plan",
    "search influencers under 100k followers",
  ];

  return (
    // center the chatbar and constrain width
    <div className="fixed left-0 right-0 bottom-6 z-50 pointer-events-auto flex justify-center px-4">
      <div className="w-full max-w-[720px] rounded-full bg-zinc-900/95 border border-zinc-800 px-3 py-2 flex items-center gap-3 shadow-lg">
        <div className="flex-1">
          <PlaceholdersAndVanishInput
            placeholders={placeholders}
            loading={loading}
            onChange={(e) => setValue(e.target.value)}
            onSubmit={(e) => {
              e.preventDefault();
              onSend();
            }}
          />
        </div>
      </div>

      {pendingModId && <div className="absolute bottom-[-1.5rem] text-xs text-gray-400 mt-2 text-center">Working on your request…</div>}
    </div>
  );
}