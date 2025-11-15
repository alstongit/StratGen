import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ContainerScroll } from "@/components/ui/container-scroll-animation";

export default function Landing() {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [index, setIndex] = useState(0);
  const slides = 2;
  const autoplayRef = useRef<number | null>(null);

  useEffect(() => {
    const el = document.getElementById("year");
    if (el) el.textContent = String(new Date().getFullYear());
  }, []);

  const startAutoplay = () => {
    stopAutoplay();
    autoplayRef.current = window.setInterval(() => {
      setIndex((i) => (i + 1) % slides);
    }, 6000);
  };
  const stopAutoplay = () => {
    if (autoplayRef.current) {
      window.clearInterval(autoplayRef.current);
      autoplayRef.current = null;
    }
  };

  useEffect(() => {
    startAutoplay();
    return stopAutoplay;
  }, []);

  useEffect(() => {
    // update indicators (keep parity with original)
    document.querySelectorAll(".carousel-indicator").forEach((el, i) => {
      el.classList.toggle("bg-white", i === index);
      el.classList.toggle("bg-white/30", i !== index);
    });
  }, [index]);

  const openMenu = () => setMobileOpen(true);
  const closeMenu = () => setMobileOpen(false);

  const handleNavigateLogin = (e?: React.MouseEvent) => {
    e?.preventDefault();
    navigate("/login");
  };

  const handleRequestAccess: React.FormEventHandler = (e) => {
    e.preventDefault();
    alert("Thanks — we will be in touch shortly!");
  };

  return (
    <div
      className="antialiased text-white bg-black selection:bg-white/20 min-h-screen overflow-x-hidden"
      style={{
        fontFamily:
          "Poppins, Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif",
      }}
    >
      {/* Backdrop */}
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div
          className="absolute -top-32 left-1/2 -translate-x-1/2 w-[900px] h-[900px] blur-3xl opacity-30"
          style={{
            background:
              "radial-gradient(50% 50% at 50% 50%, rgba(59,130,246,0.15), rgba(16,185,129,0.06) 45%, transparent 70%)",
          }}
        />
        <div
          className="absolute bottom-[-200px] right-[-200px] w-[700px] h-[700px] blur-3xl opacity-20"
          style={{
            background:
              "radial-gradient(50% 50% at 50% 50%, rgba(168,85,247,0.18), transparent 60%)",
          }}
        />
      </div>

      {/* Header */}
      <header className="relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex items-center justify-between py-6">
            <a
              href="#"
              onClick={(e) => e.preventDefault()}
              className="inline-flex items-center gap-2"
            >
              <div className="flex items-center justify-center h-9 w-9 rounded-md bg-white/5 border border-white/10">
                <span className="text-sm font-semibold tracking-tight">SG</span>
              </div>
              <span className="text-[15px] tracking-tight font-medium text-white/90">
                StratGen
              </span>
            </a>

            <div className="hidden md:flex items-center gap-2 rounded-full bg-white/5 border border-white/10 backdrop-blur px-1.5 py-1.5">
              <a
                href="#product"
                className="px-3 py-1.5 text-sm text-white/80 hover:text-white transition"
              >
                Product
              </a>
              <a
                href="#how"
                className="px-3 py-1.5 text-sm text-white/80 hover:text-white transition"
              >
                How it works
              </a>
              <a
                href="#pricing"
                className="px-3 py-1.5 text-sm text-white/80 hover:text-white transition"
              >
                Pricing
              </a>
              <a
                href="#faq"
                className="px-3 py-1.5 text-sm text-white/80 hover:text-white transition"
              >
                FAQ
              </a>
              <div className="h-6 w-px bg-white/10 mx-1" />
              <a
                href="#"
                onClick={handleNavigateLogin}
                className="px-3 py-1.5 text-sm text-white/80 hover:text-white transition"
              >
                Sign in
              </a>
              <a
                href="#cta"
                onClick={handleNavigateLogin}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 hover:bg-white/15 border border-white/10 text-sm text-white/90 transition"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="h-[18px] w-[18px]"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M3 12h12" />
                  <path d="m11 6 6 6-6 6" />
                </svg>
                Launch app
              </a>
            </div>

            <button
              id="mobileMenuToggle"
              onClick={openMenu}
              className="md:hidden inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-5 w-5"
              >
                <path d="M4 6h16" />
                <path d="M4 12h16" />
                <path d="M4 18h16" />
              </svg>
              Menu
            </button>
          </nav>


          {/* Hero */}
          <section className="text-center pt-8 sm:pt-12 md:pt-10 pb-16 md:pb-24 relative">
            {/* Backdrop gradients */}
            <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
              <div
                className="absolute -top-24 left-1/2 -translate-x-1/2 w-[900px] h-[900px] rounded-full blur-3xl opacity-30"
                style={{
                  background:
                    "radial-gradient(50% 50% at 50% 50%, rgba(16,185,129,0.20), rgba(59,130,246,0.10) 45%, transparent 70%)",
                }}
              />
              <div
                className="absolute -bottom-24 right-1/3 w-[600px] h-[600px] rounded-full blur-3xl opacity-20"
                style={{
                  background:
                    "radial-gradient(50% 50% at 50% 50%, rgba(168,85,247,0.18), transparent 65%)",
                }}
              />
            </div>

            <div className="flex flex-col overflow-hidden">
              <ContainerScroll
                /* Slight top offset inside scroll to keep CTAs fully visible */
                titleComponent={
                  <>
                    {/* Reviews / avatars */}
                    <div className="flex items-center justify-center gap-4">
                      <div className="flex -space-x-3">
                        <img
                          src="https://images.unsplash.com/photo-1531427186611-ecfd6d936c79?q=80&w=200&auto=format&fit=crop"
                          className="w-9 h-9 rounded-full ring-2 ring-black/60 object-cover"
                          alt=""
                        />
                        <img
                          src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=200&auto=format&fit=crop"
                          className="w-9 h-9 rounded-full ring-2 ring-black/60 object-cover"
                          alt=""
                        />
                        <img
                          src="https://images.unsplash.com/photo-1517841905240-472988babdf9?q=80&w=200&auto=format&fit=crop"
                          className="w-9 h-9 rounded-full ring-2 ring-black/60 object-cover"
                          alt=""
                        />
                        <img
                          src="https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?q=80&w=200&auto=format&fit=crop"
                          className="w-9 h-9 rounded-full ring-2 ring-black/60 object-cover"
                          alt=""
                        />
                        <img
                          src="https://images.unsplash.com/photo-1527980965255-d3b416303d12?q=80&w=200&auto=format&fit=crop"
                          className="w-9 h-9 rounded-full ring-2 ring-black/60 object-cover"
                          alt=""
                        />
                      </div>
                      <div className="flex flex-col items-start">
                        <div className="flex items-center text-amber-300">
                          {Array.from({ length: 4 }).map((_, i) => (
                            <svg
                              key={i}
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-4 w-4"
                              viewBox="0 0 24 24"
                              fill="currentColor"
                            >
                              <path d="m12 .587 3.668 7.431L24 9.753l-6 5.853L19.335 24 12 19.897 4.665 24 6 15.606 0 9.753l8.332-1.735z" />
                            </svg>
                          ))}
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-4 w-4 text-white/30"
                            viewBox="0 0 24 24"
                            fill="currentColor"
                          >
                            <path d="m12 .587 3.668 7.431L24 9.753l-6 5.853L19.335 24 12 19.897 4.665 24 6 15.606 0 9.753l8.332-1.735z" />
                          </svg>
                        </div>
                        <p className="text-xs text-white/70 mt-1">
                          Loved by growth teams at 1,200+ brands
                        </p>
                      </div>
                    </div>

                    <h1 className="mt-6 text-4xl sm:text-6xl md:text-7xl tracking-tight font-semibold">
                      Generate complete campaigns from a single brief.
                    </h1>
                    <p className="max-w-2xl mx-auto mt-6 text-base sm:text-lg text-white/70">
                      StratGen turns high-level goals into a full campaign
                      package—moodboard, messaging, assets, influencer picks, and
                      execution plans—ready to ship across channels.
                    </p>

                    <div
                      id="cta"
                      className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3"
                    >
                      <a
                        onClick={handleNavigateLogin}
                        href="#create"
                        className="group relative inline-flex items-center justify-center gap-2 min-w-[160px] px-5 py-3 rounded-full bg-emerald-400 text-black text-sm font-medium hover:bg-emerald-300 transition"
                      >
                        Create a campaign
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="18"
                          height="18"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.5"
                          className="h-[18px] w-[18px]"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M5 12h14" />
                          <path d="m12 5 7 7-7 7" />
                        </svg>
                      </a>
                      <a
                        href="#"
                        className="inline-flex items-center gap-2 px-5 py-3 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 backdrop-blur text-sm text-white/90 transition"
                      >
                        Watch demo
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="18"
                          height="18"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.5"
                          className="h-[18px] w-[18px]"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <polygon points="5 3 19 12 5 21 5 3" />
                        </svg>
                      </a>
                    </div>
                  </>
                }
              >
                {/* Hero mock (scroll content) */}
                <div className="relative  mx-auto max-w-5xl">
                  <div className="relative rounded-2xl border border-white/10 bg-white/5 backdrop-blur overflow-hidden">
                    <div className="flex items-center justify-between px-4 sm:px-5 py-3 border-b border-white/10">
                      <div className="flex items-center gap-2">
                        <div className="h-2.5 w-2.5 rounded-full bg-rose-400/70" />
                        <div className="h-2.5 w-2.5 rounded-full bg-amber-300/70" />
                        <div className="h-2.5 w-2.5 rounded-full bg-emerald-300/70" />
                      </div>
                      <div className="hidden sm:flex items-center gap-2 text-xs text-white/70">
                        <span className="px-2 py-1 rounded-md bg-white/5 border border-white/10">
                          Autonomous
                        </span>
                        <span className="px-2 py-1 rounded-md bg-white/5 border border-white/10">
                          Brand-safe
                        </span>
                        <span className="px-2 py-1 rounded-md bg-white/5 border border-white/10">
                          Multi-channel
                        </span>
                      </div>
                      <button className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-white/5 hover:bg-white/10 border border-white/10 text-xs transition">
                        Export
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-12 gap-3 p-3 sm:p-4">
                      {/* Visual directions */}
                      <div className="md:col-span-6 lg:col-span-7 rounded-xl border border-white/10 bg-white/5 overflow-hidden">
                        <div className="flex items-center justify-between px-3 py-2 border-b border-white/10">
                          <div className="flex items-center gap-2">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="18"
                              height="18"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="1.5"
                              className="h-[18px] w-[18px]"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            >
                              <rect width="18" height="14" x="3" y="5" rx="2" />
                              <path d="m3 17 6-6 4 4 5-5" />
                            </svg>
                            <span className="text-xs font-medium">
                              Visual directions
                            </span>
                          </div>
                          <span className="text-[11px] text-white/60">
                            6 concepts
                          </span>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 p-2">
                          <img
                            className="aspect-[4/3] w-full object-cover rounded-lg border border-white/10"
                            src="https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=600&auto=format&fit=crop"
                            alt=""
                          />
                          <img
                            className="aspect-[4/3] w-full object-cover rounded-lg border border-white/10"
                            src="https://images.unsplash.com/photo-1545239351-1141bd82e8a6?q=80&w=600&auto=format&fit=crop"
                            alt=""
                          />
                          <img
                            className="aspect-[4/3] w-full object-cover rounded-lg border border-white/10"
                            src="https://images.unsplash.com/photo-1558769132-cb1aea458c5e?q=80&w=600&auto=format&fit=crop"
                            alt=""
                          />
                          <img
                            className="aspect-[4/3] w-full object-cover rounded-lg border border-white/10"
                            src="https://images.unsplash.com/photo-1545235617-9465d2a55698?q=80&w=600&auto=format&fit=crop"
                            alt=""
                          />
                          <img
                            className="aspect-[4/3] w-full object-cover rounded-lg border border-white/10"
                            src="https://images.unsplash.com/photo-1621619856624-42fd193a0661?w=1080&q=80"
                            alt=""
                          />
                          <img
                            className="aspect-[4/3] w-full object-cover rounded-lg border border-white/10"
                            src="https://images.unsplash.com/photo-1642615835477-d303d7dc9ee9?w=1080&q=80"
                            alt=""
                          />
                        </div>
                      </div>

                      {/* Messaging & copy */}
                      <div className="md:col-span-6 lg:col-span-5 rounded-xl border border-white/10 bg-white/5 overflow-hidden">
                        <div className="flex items-center justify-between px-3 py-2 border-b border-white/10">
                          <div className="flex items-center gap-2">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="18"
                              height="18"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="1.5"
                              className="h-[18px] w-[18px]"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            >
                              <path d="M4 20h16" />
                              <path d="M6 4h12" />
                              <path d="M8 8h8" />
                              <path d="M10 12h6" />
                            </svg>
                            <span className="text-xs font-medium">
                              Messaging &amp; copy
                            </span>
                          </div>
                          <span className="text-[11px] text-white/60">
                            9 assets
                          </span>
                        </div>
                        <div className="p-3 grid gap-2">
                          <div className="rounded-lg border border-white/10 bg-black/30 p-3 hover:bg-black/20 transition">
                            <p className="text-[13px] text-white/80">
                              Headline · “Launch faster. Spend smarter.”
                            </p>
                            <p className="text-[12px] text-white/60 mt-1">
                              Primary hook variants A/B for Paid Social.
                            </p>
                          </div>
                          <div className="rounded-lg border border-white/10 bg-black/30 p-3 hover:bg-black/20 transition">
                            <p className="text-[13px] text-white/80">
                              Email · 3-step nurture sequence
                            </p>
                            <p className="text-[12px] text-white/60 mt-1">
                              Subject lines, body, CTAs tailored by segment.
                            </p>
                          </div>
                          <div className="rounded-lg border border-white/10 bg-black/30 p-3 hover:bg-black/20 transition">
                            <p className="text-[13px] text-white/80">
                              Landing · Value props + hero copy
                            </p>
                            <p className="text-[12px] text-white/60 mt-1">
                              SEO-safe, brand-aligned, conversion-first.
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Influencer graph */}
                      <div className="md:col-span-6 lg:col-span-4 rounded-xl border border-white/10 bg-white/5 overflow-hidden">
                        <div className="flex items-center justify-between px-3 py-2 border-b border-white/10">
                          <div className="flex items-center gap-2">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="18"
                              height="18"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="1.5"
                              className="h-[18px] w-[18px]"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            >
                              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                              <circle cx="9" cy="7" r="4" />
                              <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                            </svg>
                            <span className="text-xs font-medium">
                              Influencer graph
                            </span>
                          </div>
                          <span className="text-[11px] text-white/60">
                            12 matches
                          </span>
                        </div>
                        <div className="p-3 grid gap-2">
                          <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-black/30 p-3">
                            <img
                              src="https://images.unsplash.com/photo-1527980965255-d3b416303d12?q=80&w=200&auto=format&fit=crop"
                              className="w-8 h-8 rounded-full object-cover"
                              alt=""
                            />
                            <div className="text-xs">
                              <p className="text-white/90">
                                Alex Rivera · Tech creator
                              </p>
                              <p className="text-white/60">
                                1.2M reach · 4.6% ER · TikTok/YouTube
                              </p>
                            </div>
                            <span className="ml-auto text-[11px] px-2 py-0.5 rounded bg-emerald-400/15 border border-emerald-400/30 text-emerald-200">
                              FIT 92
                            </span>
                          </div>
                          <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-black/30 p-3">
                            <img
                              src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=200&auto=format&fit=crop"
                              className="w-8 h-8 rounded-full object-cover"
                              alt=""
                            />
                            <div className="text-xs">
                              <p className="text-white/90">Maya Chen · Lifestyle</p>
                              <p className="text-white/60">
                                680k reach · 5.1% ER · IG/Shorts
                              </p>
                            </div>
                            <span className="ml-auto text-[11px] px-2 py-0.5 rounded bg-emerald-400/15 border border-emerald-400/30 text-emerald-200">
                              FIT 88
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Channel plan & calendar */}
                      <div className="md:col-span-6 lg:col-span-8 rounded-xl border border-white/10 bg-white/5 overflow-hidden">
                        <div className="flex items-center justify-between px-3 py-2 border-b border-white/10">
                          <div className="flex items-center gap-2">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="18"
                              height="18"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="1.5"
                              className="h-[18px] w-[18px]"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            >
                              <rect width="18" height="18" x="3" y="4" rx="2" />
                              <path d="M16 2v4" />
                              <path d="M8 2v4" />
                              <path d="M3 10h18" />
                            </svg>
                            <span className="text-xs font-medium">
                              Channel plan &amp; calendar
                            </span>
                          </div>
                          <span className="text-[11px] text-white/60">
                            Auto-scheduled
                          </span>
                        </div>
                        <div className="p-3 grid sm:grid-cols-2 gap-2">
                          <div className="rounded-lg border border-white/10 bg-black/30 p-3">
                            <p className="text-[12px] text-white/60">
                              Week 1 · Awareness
                            </p>
                            <p className="text-sm text-white/90 mt-1">
                              Paid Social (Meta/TikTok), UGC, OOH tests
                            </p>
                          </div>
                          <div className="rounded-lg border border-white/10 bg-black/30 p-3">
                            <p className="text-[12px] text-white/60">
                              Week 2 · Consideration
                            </p>
                            <p className="text-sm text-white/90 mt-1">
                              YouTube pre-roll, retargeting, creator posts
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="pointer-events-none absolute inset-0 rounded-2xl ring-1 ring-white/10" />
                  </div>
                </div>
              </ContainerScroll>
            </div>
          </section>

        </div>
      </header>

      {/* Featured In */}
      <section className="relative mt-6 sm:mt-0">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-12">
          <p className="text-center text-sm text-white/50">Featured by</p>
          <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-8 items-center justify-items-center">
            {[
              "GROWTH WEEKLY",
              "PERFORMANCE LAB",
              "CREATOR HUB",
              "AD OPS DAILY",
              "MARTECH",
              "STACK REPORT",
            ].map((t) => (
              <span
                key={t}
                className="text-white/60 text-sm tracking-tight px-3 py-2 rounded-md border border-white/10 bg-white/5"
              >
                {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Value Section */}
      <section id="product" className="relative">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl md:text-5xl tracking-tight font-semibold">
                Confirm strategy. Receive a full campaign package.
              </h2>
              <p className="mt-4 text-base text-white/70">
                Go from brief to assets in hours, not weeks. Align on positioning
                and guardrails with AI, then automatically generate visuals, copy,
                influencer lists, and a channel-by-channel execution plan.
              </p>
              <div className="mt-6 flex items-center gap-3">
                <a
                  href="#how"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm transition"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    className="h-[18px] w-[18px]"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <rect x="2" y="2" width="20" height="16" rx="2" />
                    <path d="M7 2v16" />
                    <path d="M2 7h20" />
                  </svg>
                  See how it works
                </a>
                <button
                  onClick={handleNavigateLogin}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-400 hover:bg-emerald-300 text-sm text-black transition"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    className="h-[18px] w-[18px]"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 13v8l-4-4" />
                    <path d="m12 21 4-4" />
                    <path d="M4.393 15.269A7 7 0 1 1 15.71 8h1.79A4.5 4.5 0 0 1 19.936 16.284" />
                  </svg>
                  Start free
                </button>
              </div>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1553877522-43269d4ea984?q=80&w=1400&auto=format&fit=crop"
                className="w-full aspect-[4/3] object-cover rounded-2xl border border-white/10"
                alt="Campaign board"
              />
              <div className="pointer-events-none absolute inset-0 rounded-2xl ring-1 ring-white/10" />
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8">
            <div>
              <p className="text-sm text-white/50">What you get</p>
              <h3 className="text-3xl sm:text-4xl md:text-5xl tracking-tight font-semibold">
                Everything to launch and scale
              </h3>
              <p className="mt-3 text-base text-white/70">
                Strategy co-pilot, creative generation, and automated
                execution—aligned to your brand.
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Big feature */}
            <div className="group relative md:col-span-2 md:row-span-2 rounded-2xl border border-white/10 bg-white/5 overflow-hidden">
              <div className="relative">
                <img
                  src="https://images.unsplash.com/photo-1556157382-97eda2d62296?q=80&w=1600&auto=format&fit=crop"
                  className="w-full aspect-video object-cover"
                  alt=""
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
              </div>
              <div className="p-5 sm:p-6">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center px-2 py-0.5 text-[11px] rounded-full border border-emerald-400/30 bg-emerald-400/15 text-emerald-200">
                    NEW
                  </span>
                  <span className="text-xs text-white/60">Strategy Engine</span>
                </div>
                <h4 className="mt-3 text-2xl sm:text-3xl tracking-tight font-semibold">
                  From brief to aligned strategy in minutes
                </h4>
                <p className="mt-2 text-sm sm:text-base text-white/70">
                  Paste your goals and constraints. StratGen proposes audience,
                  positioning, and channel mix—then iterates with you to lock the
                  plan.
                </p>
                <div className="mt-5 flex flex-wrap items-center gap-3">
                  <a
                    href="#"
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-white/90"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="18"
                      height="18"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      className="h-[18px] w-[18px]"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M3 12h18" />
                      <path d="m11 5 7 7-7 7" />
                    </svg>
                    Explore strategies
                  </a>
                  <button
                    onClick={handleNavigateLogin}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-400 hover:bg-emerald-300 text-sm text-black"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="18"
                      height="18"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      className="h-[18px] w-[18px]"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="m22 2-7 20-4-9-9-4Z" />
                      <path d="M22 2 11 13" />
                    </svg>
                    Generate now
                  </button>
                </div>
              </div>
            </div>

            {/* Right column cards */}
            <div className="rounded-2xl border border-white/10 bg-white/5">
              <div className="p-5 sm:p-6">
                <div className="flex items-center justify-between">
                  <h5 className="text-xl tracking-tight font-medium flex items-center gap-2">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="18"
                      height="18"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      className="h-[18px] w-[18px]"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
                    </svg>
                    Brand guardrails
                  </h5>
                  <span className="inline-flex items-center px-2 py-0.5 text-[11px] rounded-full border border-sky-400/30 bg-sky-400/15 text-sky-200">
                    SAFE
                  </span>
                </div>
                <p className="mt-2 text-sm text-white/70">
                  Upload voice, terms, and do-not-say lists. Guardrails flow into
                  every asset and channel.
                </p>
                <div className="mt-4 rounded-lg overflow-hidden border border-white/10">
                  <img
                    src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=1000&auto=format&fit=crop"
                    className="w-full aspect-video object-cover"
                    alt=""
                  />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5">
              <div className="p-5 sm:p-6">
                <div className="flex items-center justify-between">
                  <h5 className="text-xl tracking-tight font-medium flex items-center gap-2">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="18"
                      height="18"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      className="h-[18px] w-[18px]"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M21 10H3" />
                      <path d="M8 2v4" />
                      <path d="M16 2v4" />
                      <rect width="18" height="18" x="3" y="4" rx="2" />
                    </svg>
                    Channel calendar
                  </h5>
                  <span className="inline-flex items-center px-2 py-0.5 text-[11px] rounded-full border border-purple-400/30 bg-purple-400/15 text-purple-200">
                    AUTO
                  </span>
                </div>
                <p className="mt-2 text-sm text-white/70">
                  Auto-creates schedules, budgets, and pacing with smart
                  constraints.
                </p>
                <div className="mt-4 rounded-lg overflow-hidden border border-white/10">
                  <img
                    src="https://images.unsplash.com/photo-1635151227785-429f420c6b9d?w=1080&q=80"
                    className="w-full aspect-video object-cover"
                    alt=""
                  />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5">
              <div className="p-5 sm:p-6">
                <h5 className="text-lg tracking-tight font-medium flex items-center gap-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    className="h-[18px] w-[18px]"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 8V4H8" />
                    <rect x="8" y="4" width="8" height="8" rx="2" />
                    <path d="M20 16v4h-4" />
                    <rect x="12" y="12" width="8" height="8" rx="2" />
                  </svg>
                  Creative assets
                </h5>
                <p className="mt-2 text-sm text-white/70">
                  Visuals, ad sets, headlines, long/short copy, and landing
                  sections.
                </p>
                <div className="mt-4 rounded-lg overflow-hidden border border-white/10">
                  <img
                    src="https://images.unsplash.com/photo-1515879218367-8466d910aaa4?q=80&w=1000&auto=format&fit=crop"
                    className="w-full aspect-video object-cover"
                    alt=""
                  />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5">
              <div className="p-5 sm:p-6">
                <h5 className="text-lg tracking-tight font-medium flex items-center gap-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    className="h-[18px] w-[18px]"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                  </svg>
                  Influencer graph
                </h5>
                <p className="mt-2 text-sm text-white/70">
                  Ranked creator matches by fit, reach, and brand safety.
                </p>
                <div className="mt-4 rounded-lg overflow-hidden border border-white/10">
                  <img
                    src="https://images.unsplash.com/photo-1542626991-cbc4e32524cc?q=80&w=1000&auto=format&fit=crop"
                    className="w-full aspect-video object-cover"
                    alt=""
                  />
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5">
              <div className="p-5 sm:p-6">
                <h5 className="text-lg tracking-tight font-medium flex items-center gap-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    className="h-[18px] w-[18px]"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M10 13v-1a3 3 0 0 1 3-3h1" />
                    <path d="M14 13v-1a3 3 0 0 0-3-3h-1" />
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                  </svg>
                  Collaboration
                </h5>
                <p className="mt-2 text-sm text-white/70">
                  Share boards, collect feedback, and approve variants with
                  stakeholders.
                </p>
                <div className="mt-4 rounded-lg overflow-hidden border border-white/10">
                  <img
                    src="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?q=80&w=1000&auto=format&fit=crop"
                    className="w-full aspect-video object-cover"
                    alt=""
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="relative">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
          <div className="max-w-3xl mx-auto text-center">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-[11px] text-white/70 bg-white/5 border border-white/10 backdrop-blur">
              Workflow
            </span>
            <h3 className="mt-4 text-3xl sm:text-4xl md:text-5xl tracking-tight font-semibold">
              From brief to launch in four steps
            </h3>
            <p className="mt-3 text-base text-white/70">
              A guided path where you stay in control—AI handles the heavy
              lifting.
            </p>
          </div>
          <div className="mt-10 grid md:grid-cols-4 gap-4">
            {[
              {
                n: 1,
                t: "Paste brief",
                d: "Objectives, audience, constraints.",
                chip: "“Grow trials +25% in Q4 for Gen Z...”",
              },
              {
                n: 2,
                t: "Align strategy",
                d: "Review positioning and channel mix.",
                chip: "Primary channel: TikTok, YT pre-roll...",
              },
              {
                n: 3,
                t: "Approve moodboard",
                d: "Lock creative directions and copy.",
                chip: "3 visual concepts · 9 copy sets",
              },
              {
                n: 4,
                t: "Publish assets",
                d: "Export or push to your stack.",
                chip: "Meta, Google, TikTok, Sheets...",
              },
            ].map((s) => (
              <div
                key={s.n}
                className="rounded-xl border border-white/10 bg-white/5 p-5"
              >
                <div className="flex items-center gap-2 text-sm text-white/80">
                  <span className="h-5 w-5 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                    {s.n}
                  </span>
                  {s.t}
                </div>
                <p className="mt-2 text-sm text-white/70">{s.d}</p>
                <div className="mt-3 rounded-lg border border-white/10 bg-black/30 p-3 text-[12px] text-white/70">
                  {s.chip}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Community / Testimonials */}
      <section
        className="relative"
        id="community"
        onMouseEnter={stopAutoplay}
        onMouseLeave={startAutoplay}
      >
        <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
          <div
            className="absolute -top-20 left-1/4 w-[700px] h-[700px] rounded-full blur-3xl opacity-25"
            style={{
              background:
                "radial-gradient(50% 50% at 50% 50%, rgba(59,130,246,0.15), rgba(16,185,129,0.10) 40%, transparent 70%)",
            }}
          />
          <div
            className="absolute -bottom-28 right-1/4 w-[600px] h-[600px] rounded-full blur-3xl opacity-25"
            style={{
              background:
                "radial-gradient(50% 50% at 50% 50%, rgba(236,72,153,0.16), transparent 60%)",
            }}
          />
        </div>
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-[11px] text-white/70 bg-white/5 border border-white/10 backdrop-blur">
              Community
            </span>
            <h3 className="mt-4 text-3xl sm:text-4xl md:text-5xl tracking-tight font-semibold">
              What teams say about StratGen
            </h3>
            <p className="mt-3 text-base text-white/70">
              From scrappy startups to enterprise growth orgs.
            </p>
          </div>

          <div className="mt-10 relative">
            <div
              className="overflow-hidden"
              style={{
                maskImage:
                  "linear-gradient(to right, transparent, black 10%, black 90%, transparent)",
                WebkitMaskImage:
                  "linear-gradient(to right, transparent, black 10%, black 90%, transparent)",
              }}
            >
              <div
                id="testimonialCarousel"
                className="flex transition-transform duration-500 ease-out"
                style={{ transform: `translateX(-${index * 100}%)` }}
              >
                {/* Slide 1 */}
                <div className="w-full flex-shrink-0">
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      {
                        img: "https://images.unsplash.com/photo-1527980965255-d3b416303d12?q=80&w=200&auto=format&fit=crop",
                        name: "Jordan Lee",
                        role: "Head of Growth, DTC",
                        quote:
                          "“We used to juggle 5 tools and a creative agency. StratGen got us to launch-ready assets in two days.”",
                      },
                      {
                        img: "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?q=80&w=200&auto=format&fit=crop",
                        name: "Priya Natarajan",
                        role: "VP Marketing, SaaS",
                        quote:
                          "“The moodboard workflow keeps stakeholders aligned. Edits are fast and brand-safe.”",
                      },
                      {
                        img: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=200&auto=format&fit=crop",
                        name: "Sam Carter",
                        role: "Founder, Mobile App",
                        quote:
                          "“Creator recommendations were on-point. CPA dropped 18% in the first sprint.”",
                      },
                    ].map((t) => (
                      <div
                        key={t.name}
                        className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur"
                      >
                        <div className="flex items-center gap-3">
                          <img
                            src={t.img}
                            className="w-9 h-9 rounded-full object-cover ring-2 ring-black/60"
                            alt=""
                          />
                          <div>
                            <p className="text-sm font-semibold tracking-tight">
                              {t.name}
                            </p>
                            <p className="text-xs text-white/60 mt-0.5">
                              {t.role}
                            </p>
                          </div>
                        </div>
                        <p className="mt-3 text-sm text-white/80">{t.quote}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Slide 2 */}
                <div className="w-full flex-shrink-0">
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      {
                        img: "https://images.unsplash.com/photo-1517841905240-472988babdf9?q=80&w=200&auto=format&fit=crop",
                        name: "Diego Martinez",
                        role: "Performance Lead",
                        quote:
                          "“Channel calendars with pacing and budgets saved us countless hours.”",
                      },
                      {
                        img: "https://images.unsplash.com/photo-1531427186611-ecfd6d936c79?q=80&w=200&auto=format&fit=crop",
                        name: "Ana Sousa",
                        role: "Agency Partner",
                        quote:
                          "“We ship more creative now without adding headcount.”",
                      },
                      {
                        img: "https://images.unsplash.com/photo-1527980965255-d3b416303d12?q=80&w=200&auto=format&fit=crop",
                        name: "Emily Zhang",
                        role: "Lifecycle Marketing",
                        quote:
                          "“Copy variants were surprisingly on-brand and ready to test.”",
                      },
                    ].map((t) => (
                      <div
                        key={t.name}
                        className="rounded-2xl border border-white/10 bg-white/5 p-6"
                      >
                        <div className="flex items-center gap-3">
                          <img
                            src={t.img}
                            className="w-9 h-9 rounded-full object-cover ring-2 ring-black/60"
                            alt=""
                          />
                          <div>
                            <p className="text-sm font-semibold tracking-tight">
                              {t.name}
                            </p>
                            <p className="text-xs text-white/60 mt-0.5">
                              {t.role}
                            </p>
                          </div>
                        </div>
                        <p className="mt-3 text-sm text-white/80">{t.quote}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between mt-6">
              <button
                id="prevBtn"
                onClick={() => setIndex((i) => (i - 1 + slides) % slides)}
                className="inline-flex items-center justify-center w-10 h-10 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="h-5 w-5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="m15 18-6-6 6-6" />
                </svg>
              </button>
              <div className="flex items-center gap-2">
                <button
                  className="carousel-indicator w-2 h-2 rounded-full bg-white"
                  onClick={() => setIndex(0)}
                  aria-label="Slide 1"
                />
                <button
                  className="carousel-indicator w-2 h-2 rounded-full bg-white/30 hover:bg-white/50 transition"
                  onClick={() => setIndex(1)}
                  aria-label="Slide 2"
                />
              </div>
              <button
                id="nextBtn"
                onClick={() => setIndex((i) => (i + 1) % slides)}
                className="inline-flex items-center justify-center w-10 h-10 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="h-5 w-5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="m9 18 6-6-6-6" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="relative sm:p-8 sm:mx-8 mt-6">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="max-w-5xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/80">
              <span className="h-1.5 w-1.5 rounded-full bg-white" />
              <span className="text-xs font-normal">Pricing</span>
            </div>
            <h3 className="text-[40px] sm:text-6xl leading-[0.95] tracking-tight mt-4 font-semibold">
              Simple, scalable plans
            </h3>
            <p className="mt-3 text-sm sm:text-base text-white/70 max-w-2xl mx-auto">
              Start free, upgrade when you’re ready. Cancel anytime.
            </p>
          </div>

          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Free */}
            <article className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-6">
              <div className="relative text-center">
                <h4 className="text-xl tracking-tight font-medium">Free</h4>
                <div className="mt-3 flex items-end justify-center gap-2">
                  <p className="text-4xl sm:text-5xl tracking-tight">$0</p>
                  <span className="text-white/70 text-sm mb-1">/ forever</span>
                </div>
                <p className="mt-3 text-sm text-white/70">
                  Explore StratGen with core features.
                </p>
                <div className="mt-4 flex flex-wrap gap-2 justify-center">
                  <span className="px-3 py-1 text-xs rounded-lg bg-white/5 border border-white/10 text-white/80">
                    1 campaign/mo
                  </span>
                  <span className="px-3 py-1 text-xs rounded-lg bg-white/5 border border-white/10 text-white/80">
                    Basic assets
                  </span>
                </div>
              </div>
              <ul className="mt-5 space-y-3">
                {[
                  "Strategy Engine (lite)",
                  "Copy + visual samples",
                  "1 user",
                ].map((f) => (
                  <li key={f} className="flex items-center gap-3">
                    <span className="h-5 w-5 flex items-center justify-center rounded-full bg-white/5 border border-white/10">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="14"
                        height="14"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        className="h-3.5 w-3.5 text-emerald-400"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    </span>
                    <span className="text-sm text-white/90">{f}</span>
                  </li>
                ))}
              </ul>
              <button
                onClick={handleNavigateLogin}
                className="mt-6 inline-flex w-full items-center justify-center gap-2 h-11 rounded-xl bg-emerald-400 text-black text-sm font-medium hover:bg-emerald-300 transition"
              >
                Get started
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="h-4.5 w-4.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M7 7h10v10" />
                  <path d="M7 17 17 7" />
                </svg>
              </button>
            </article>

            {/* Pro */}
            <article className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-6">
              <span className="absolute top-4 right-4 inline-flex items-center px-3 py-1 rounded-lg text-xs text-white/80 bg-white/5 border border-white/10">
                Most popular
              </span>
              <div className="relative text-center">
                <h4 className="text-xl tracking-tight font-medium">Pro</h4>
                <div className="mt-3 flex items-end justify-center gap-2">
                  <p className="text-4xl sm:text-5xl tracking-tight">$79</p>
                  <span className="text-white/70 text-sm mb-1">/ month</span>
                </div>
                <p className="mt-3 text-sm text-white/70">
                  Everything you need to launch campaigns.
                </p>
                <div className="mt-4 flex flex-wrap gap-2 justify-center">
                  {["Unlimited boards", "Full assets", "Creator graph"].map(
                    (t) => (
                      <span
                        key={t}
                        className="px-3 py-1 text-xs rounded-lg bg-white/5 border border-white/10 text-white/80"
                      >
                        {t}
                      </span>
                    )
                  )}
                </div>
              </div>
              <ul className="mt-5 space-y-3">
                {[
                  "Advanced Strategy Engine",
                  "Asset generation (visual + copy)",
                  "Influencer recommendations",
                  "Channel plan + calendar",
                  "3 seats",
                ].map((f) => (
                  <li key={f} className="flex items-center gap-3">
                    <span className="h-5 w-5 flex items-center justify-center rounded-full bg-white/5 border border-white/10">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="14"
                        height="14"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        className="h-3.5 w-3.5 text-emerald-400"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    </span>
                    <span className="text-sm text-white/90">{f}</span>
                  </li>
                ))}
              </ul>
              <button
                onClick={handleNavigateLogin}
                className="mt-6 inline-flex w-full items-center justify-center gap-2 h-11 rounded-xl bg-gradient-to-r from-emerald-400 to-sky-400 text-black text-sm font-medium hover:from-emerald-300 hover:to-sky-300 transition"
              >
                Upgrade to Pro
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="h-4.5 w-4.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M7 7h10v10" />
                  <path d="M7 17 17 7" />
                </svg>
              </button>
            </article>

            {/* Enterprise */}
            <article className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-6">
              <div className="relative text-center">
                <h4 className="text-xl tracking-tight font-medium">
                  Enterprise
                </h4>
                <div className="mt-3 flex items-end justify-center gap-2">
                  <p className="text-4xl sm:text-5xl tracking-tight">Custom</p>
                </div>
                <p className="mt-3 text-sm text-white/70">
                  Security, SSO, and custom workflows.
                </p>
                <div className="mt-4 flex flex-wrap gap-2 justify-center">
                  {["SSO/SAML", "Custom guardrails", "Dedicated support"].map(
                    (t) => (
                      <span
                        key={t}
                        className="px-3 py-1 text-xs rounded-lg bg-white/5 border border-white/10 text-white/80"
                      >
                        {t}
                      </span>
                    )
                  )}
                </div>
              </div>
              <ul className="mt-5 space-y-3">
                {[
                  "Custom approvals & compliance",
                  "On-prem / VPC options",
                  "Custom integrations & SLAs",
                  "Security review support (SOC 2, DPIA)",
                  "Unlimited seats · Priority support",
                ].map((f) => (
                  <li key={f} className="flex items-center gap-3">
                    <span className="h-5 w-5 flex items-center justify-center rounded-full bg-white/5 border border-white/10">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="14"
                        height="14"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        className="h-3.5 w-3.5 text-emerald-400"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    </span>
                    <span className="text-sm text-white/90">{f}</span>
                  </li>
                ))}
              </ul>
              <a
                href="#contact"
                className="mt-6 inline-flex w-full items-center justify-center gap-2 h-11 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white text-sm font-medium transition"
              >
                Contact sales
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="h-4.5 w-4.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M22 2 11 13" />
                  <path d="m22 2-7 20-4-9-9-4z" />
                </svg>
              </a>
            </article>
          </div>

          <p className="mt-6 text-center text-sm text-white/60">
            Prices in USD. Taxes may apply. Pro plan includes 14-day money-back
            guarantee.
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="relative">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
          <div className="max-w-3xl mx-auto text-center">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-[11px] text-white/70 bg-white/5 border border-white/10">
              FAQ
            </span>
            <h3 className="mt-4 text-3xl sm:text-4xl md:text-5xl tracking-tight font-semibold">
              Questions, answered
            </h3>
            <p className="mt-3 text-base text-white/70">
              Can’t find what you’re looking for? Reach out via chat or email.
            </p>
          </div>

          <div className="mt-10 grid md:grid-cols-2 gap-4">
            {[
              {
                q: "How does StratGen ensure brand safety?",
                a: "Define voice, terms, disallowed phrases, and compliance requirements. These guardrails are validated against every output with automated checks and optional human review steps.",
              },
              {
                q: "Which channels and tools do you support?",
                a: "Meta, Google, YouTube, TikTok, LinkedIn, and email. Export to Sheets/CSV/Slides and push to ad platforms with one click. Enterprise plans support custom destinations via API.",
              },
              {
                q: "Do I retain ownership of generated assets?",
                a: "Yes. You own the assets created in your workspace, subject to the terms of third‑party stock or data sources you connect.",
              },
              {
                q: "Is there a free trial for Pro?",
                a: "You can start free and upgrade any time. Pro includes a 14-day money-back guarantee to try the full workflow with your team.",
              },
            ].map((item) => (
              <details
                key={item.q}
                className="group rounded-xl border border-white/10 bg-white/5 p-5 open:bg-white/7 open:border-white/20 transition"
              >
                <summary className="flex cursor-pointer list-none items-center justify-between">
                  <h4 className="text-sm font-medium">{item.q}</h4>
                  <span className="ml-4 inline-flex h-7 w-7 items-center justify-center rounded-full bg-white/5 border border-white/10 text-white/70 group-open:rotate-45 transition">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-3.5 w-3.5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path d="M12 5v14M5 12h14" />
                    </svg>
                  </span>
                </summary>
                <p className="mt-3 text-sm text-white/70">{item.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section id="contact" className="relative">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
          <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.07] to-white/[0.03] p-8 sm:p-10 overflow-hidden">
            <div
              className="absolute -right-24 -top-24 h-72 w-72 rounded-full blur-3xl opacity-25 pointer-events-none"
              style={{
                background:
                  "radial-gradient(50% 50% at 50% 50%, rgba(16,185,129,0.35), transparent 70%)",
              }}
            />
            <div className="grid md:grid-cols-3 gap-6 relative">
              <div className="md:col-span-2">
                <h4 className="text-2xl sm:text-3xl md:text-4xl tracking-tight font-semibold">
                  Ship your next campaign in days, not weeks
                </h4>
                <p className="mt-2 text-white/70">
                  Brief StratGen and get strategy, assets, creators, and a channel
                  plan—ready to launch.
                </p>
                <div className="mt-6 flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={handleNavigateLogin}
                    className="inline-flex items-center justify-center gap-2 px-5 h-11 rounded-xl bg-emerald-400 text-black text-sm font-medium hover:bg-emerald-300 transition"
                  >
                    Start free
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="18"
                      height="18"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      className="h-4.5 w-4.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M5 12h14" />
                      <path d="m12 5 7 7-7 7" />
                    </svg>
                  </button>
                  <a
                    href="#"
                    className="inline-flex items-center justify-center gap-2 px-5 h-11 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white/90 text-sm transition"
                  >
                    Book a demo
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="18"
                      height="18"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      className="h-4.5 w-4.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M5 3l14 9-14 9V3z" />
                    </svg>
                  </a>
                </div>
              </div>

              <form className="space-y-3" onSubmit={handleRequestAccess}>
                <div>
                  <label htmlFor="email" className="sr-only">
                    Work email
                  </label>
                  <input
                    id="email"
                    type="email"
                    required
                    placeholder="Work email"
                    className="w-full h-11 px-3.5 rounded-xl bg-black/40 border border-white/10 focus:border-emerald-400/60 outline-none text-sm placeholder:text-white/40"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label htmlFor="name" className="sr-only">
                      Full name
                    </label>
                    <input
                      id="name"
                      type="text"
                      required
                      placeholder="Full name"
                      className="w-full h-11 px-3.5 rounded-xl bg-black/40 border border-white/10 focus:border-emerald-400/60 outline-none text-sm placeholder:text-white/40"
                    />
                  </div>
                  <div>
                    <label htmlFor="company" className="sr-only">
                      Company
                    </label>
                    <input
                      id="company"
                      type="text"
                      placeholder="Company (optional)"
                      className="w-full h-11 px-3.5 rounded-xl bg-black/40 border border-white/10 focus:border-emerald-400/60 outline-none text-sm placeholder:text-white/40"
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  className="w-full h-11 rounded-xl bg-gradient-to-r from-emerald-400 to-sky-400 text-black text-sm font-medium hover:from-emerald-300 hover:to-sky-300 transition"
                >
                  Request access
                </button>
                <p className="text-[11px] text-white/50">
                  By requesting access you agree to our{" "}
                  <a
                    href="#"
                    className="underline decoration-white/30 hover:decoration-white"
                  >
                    Terms
                  </a>{" "}
                  and{" "}
                  <a
                    href="#"
                    className="underline decoration-white/30 hover:decoration-white"
                  >
                    Privacy
                  </a>
                  .
                </p>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-12">
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <a
                href="#"
                onClick={(e) => e.preventDefault()}
                className="inline-flex items-center gap-2"
              >
                <div className="flex items-center justify-center h-9 w-9 rounded-md bg-white/5 border border-white/10">
                  <span className="text-sm font-semibold tracking-tight">SG</span>
                </div>
                <span className="text-[15px] tracking-tight font-medium text-white/90">
                  StratGen
                </span>
              </a>
              <p className="mt-3 text-sm text-white/60">
                AI strategist for modern growth teams.
              </p>
            </div>

            <div>
              <p className="text-sm font-medium text-white/80">Product</p>
              <ul className="mt-3 space-y-2 text-sm text-white/70">
                <li>
                  <a className="hover:text-white transition" href="#product">
                    Overview
                  </a>
                </li>
                <li>
                  <a className="hover:text-white transition" href="#how">
                    Workflow
                  </a>
                </li>
                <li>
                  <a className="hover:text-white transition" href="#pricing">
                    Pricing
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <p className="text-sm font-medium text-white/80">Company</p>
              <ul className="mt-3 space-y-2 text-sm text-white/70">
                <li>
                  <a className="hover:text-white transition" href="#community">
                    Customers
                  </a>
                </li>
                <li>
                  <a className="hover:text-white transition" href="#faq">
                    FAQ
                  </a>
                </li>
                <li>
                  <a className="hover:text-white transition" href="#contact">
                    Contact
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <p className="text-sm font-medium text-white/80">Legal</p>
              <ul className="mt-3 space-y-2 text-sm text-white/70">
                <li>
                  <a className="hover:text-white transition" href="#">
                    Terms
                  </a>
                </li>
                <li>
                  <a className="hover:text-white transition" href="#">
                    Privacy
                  </a>
                </li>
                <li>
                  <a className="hover:text-white transition" href="#">
                    Security
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-white/10 pt-6">
            <p className="text-xs text-white/50">
              © <span id="year" /> StratGen Inc. All rights reserved.
            </p>
            <div className="flex items-center gap-2">
              <a
                href="#"
                className="inline-flex items-center justify-center h-9 w-9 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition"
                aria-label="Twitter"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4.5 w-4.5"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53A4.48 4.48 0 0 0 12 7.48v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z" />
                </svg>
              </a>
              <a
                href="#"
                className="inline-flex items-center justify-center h-9 w-9 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition"
                aria-label="LinkedIn"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4.5 w-4.5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M4.98 3.5C4.98 4.88 3.86 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1 4.98 2.12 4.98 3.5zM.5 8h4V24h-4zM8 8h3.8v2.2h.06c.53-1 1.84-2.2 3.8-2.2 4.06 0 4.8 2.67 4.8 6.14V24h-4-6.6c0-1.57-.03-3.6-2.2-3.6-2.2 0-2.54 1.72-2.54 3.5V24H8z" />
                </svg>
              </a>
              <a
                href="#"
                className="inline-flex items-center justify-center h-9 w-9 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition"
                aria-label="YouTube"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4.5 w-4.5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.6 3.5 12 3.5 12 3.5s-7.6 0-9.4.6A3 3 0 0 0 .5 6.2 31.4 31.4 0 0 0 0 12a31.4 31.4 0 0 0 .6 5.8 3 3 0 0 0 2.1 2.1c1.9.6 9.3.6 9.3.6s7.6 0 9.4-.6a3 3 0 0 0 2.1-2.1A31.4 31.4 0 0 0 24 12a31.4 31.4 0 0 0-.5-5.8zM9.75 15.5v-7l6 3.5-6 3.5z" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Mobile menu */}
      <div
        id="mobileMenu"
        className={`fixed inset-0 z-50 ${mobileOpen ? "" : "hidden"}`}
      >
        <div
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={closeMenu}
        />
        <div className="relative ml-auto h-full w-[85%] max-w-sm bg-black border-l border-white/10 p-6">
          <div className="flex items-center justify-between">
            <div className="inline-flex items-center gap-2">
              <div className="flex items-center justify-center h-9 w-9 rounded-md bg-white/5 border border-white/10">
                <span className="text-sm font-semibold tracking-tight">SG</span>
              </div>
              <span className="text-[15px] tracking-tight font-medium text-white/90">
                StratGen
              </span>
            </div>
            <button
              id="mobileMenuClose"
              onClick={closeMenu}
              className="inline-flex items-center justify-center h-9 w-9 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10"
              aria-label="Close menu"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4.5 w-4.5"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
              >
                <path d="M18 6 6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <nav className="mt-6 space-y-1">
            <a
              href="#product"
              onClick={closeMenu}
              className="block px-3 py-2 rounded-lg hover:bg-white/5 text-white/90"
            >
              Product
            </a>
            <a
              href="#how"
              onClick={closeMenu}
              className="block px-3 py-2 rounded-lg hover:bg-white/5 text-white/90"
            >
              How it works
            </a>
            <a
              href="#pricing"
              onClick={closeMenu}
              className="block px-3 py-2 rounded-lg hover:bg-white/5 text-white/90"
            >
              Pricing
            </a>
            <a
              href="#faq"
              onClick={closeMenu}
              className="block px-3 py-2 rounded-lg hover:bg-white/5 text-white/90"
            >
              FAQ
            </a>
            <div className="h-px bg-white/10 my-2" />
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                handleNavigateLogin();
                closeMenu();
              }}
              className="block px-3 py-2 rounded-lg hover:bg-white/5 text-white/90"
            >
              Sign in
            </a>
            <a
              href="#cta"
              onClick={() => {
                handleNavigateLogin();
                closeMenu();
              }}
              className="mt-2 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-400 text-black text-sm font-medium hover:bg-emerald-300 transition"
            >
              Launch app
            </a>
          </nav>
        </div>
      </div>
    </div>
  );
}