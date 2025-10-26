import type { DayPost } from '@/types';
import { Card } from '@/components/ui/card';
import { Instagram, ImageIcon, Copy, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PostCardProps {
  post: DayPost;
}

export function PostCard({ post }: PostCardProps) {
  const copyContent = post.copy?.content || {};
  const imageContent = post.image?.content;

  // prefer storage_url then image_url
  const imageUrl = imageContent?.storage_url || imageContent?.image_url;

  const handleCopyCaption = () => {
    if (copyContent?.caption) navigator.clipboard.writeText(copyContent.caption);
  };

  // normalize fields coming from ContentAgent
  const caption = copyContent.caption || '';
  const description = copyContent.description || '';
  const headline = copyContent.headline || '';
  const cta = copyContent.cta || '';
  const platform = copyContent.platform || 'instagram';
  const hashtags: string[] = Array.isArray(copyContent.hashtags) ? copyContent.hashtags : [];

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      {/* Image - show entire square image without cropping */}
      {imageUrl ? (
        <div className="relative w-full aspect-square flex items-center justify-center bg-gray-50">
          <img
            src={imageUrl}
            alt={`Day ${post.day_number}`}
            className="max-w-full max-h-full object-contain"
            onError={(e) => {
              e.currentTarget.src = `https://via.placeholder.com/669x669?text=Day+${post.day_number}`;
            }}
          />
          <div className="absolute top-2 left-2 bg-black/70 text-white px-2 py-0.5 rounded-full text-sm font-medium">
            Day {post.day_number}
          </div>
        </div>
      ) : (
        <div className="w-full aspect-square flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50">
          <div className="text-center">
            <ImageIcon className="w-10 h-10 text-gray-300 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-600">Day {post.day_number}</p>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            {platform}
          </span>
          <Instagram className="w-4 h-4 text-pink-500" />
        </div>

        {copyContent ? (
          <>
            {/* optional headline (not primary) */}
            {headline && (
              <div className="text-xs text-gray-500 mb-1 line-clamp-2">{headline}</div>
            )}

            {/* caption is primary */}
            {caption && (
              <h3 className="font-semibold text-sm text-gray-900 mb-1 leading-tight">{caption}</h3>
            )}

            {/* description secondary */}
            {description && (
              <p className="text-sm text-gray-600 mb-3">{description}</p>
            )}

            {/* CTA (if present) */}
            {cta && (
              <div className="mb-3">
                <span className="text-xs font-medium text-white bg-indigo-600 px-2 py-1 rounded">{cta}</span>
              </div>
            )}

            {/* Hashtags - show all */}
            {hashtags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {hashtags.map((tag: string, i: number) => (
                  <span key={i} className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                    {tag}
                  </span>
                ))}
              </div>
            )}

            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="flex-1 text-xs" onClick={handleCopyCaption}>
                <Copy className="w-3 h-3 mr-1" /> Copy
              </Button>
              {imageUrl && (
                <Button variant="outline" size="sm" onClick={() => window.open(imageUrl, '_blank')}>
                  <ExternalLink className="w-3 h-3" />
                </Button>
              )}
            </div>
          </>
        ) : (
          <div className="text-center py-2">
            <p className="text-sm text-gray-500">Copy content pending...</p>
          </div>
        )}
      </div>
    </Card>
  );
}