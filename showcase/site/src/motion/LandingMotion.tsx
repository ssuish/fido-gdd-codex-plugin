import { useRef, type RefObject } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { MotionPathPlugin } from "gsap/MotionPathPlugin";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { prefersReducedMotion } from "./prefersReducedMotion";

gsap.registerPlugin(useGSAP, ScrollTrigger, MotionPathPlugin);

type LandingMotionProps = {
  scope: RefObject<HTMLElement | null>;
};

function revealBatch(elements: Element[]) {
  gsap.to(elements, {
    autoAlpha: 1,
    y: 0,
    duration: 0.7,
    stagger: 0.08,
    ease: "power2.out",
    overwrite: "auto",
  });
}

/**
 * Landing-only motion controller. Observes native scroll; never writes scroll position.
 * Cleanup is handled by useGSAP context revert plus matchMedia.revert().
 */
export function LandingMotion({ scope }: LandingMotionProps) {
  const ready = useRef(false);

  useGSAP(
    () => {
      const root = scope.current;
      if (!root || ready.current) return;
      ready.current = true;

      if (prefersReducedMotion()) {
        gsap.set(root.querySelectorAll("[data-reveal], [data-trace-node], [data-trace-metric]"), {
          clearProps: "all",
        });
        gsap.set(root.querySelectorAll("[data-trace-route]"), { strokeDashoffset: 0 });
        gsap.set(root.querySelectorAll("[data-trace-marker]"), { autoAlpha: 0 });
        return () => {
          ready.current = false;
        };
      }

      const mm = gsap.matchMedia();

      mm.add(
        {
          reduceMotion: "(prefers-reduced-motion: reduce)",
          coarse: "(pointer: coarse)",
          narrow: "(max-width: 767px)",
          fineWide: "(pointer: fine) and (min-width: 768px)",
        },
        (context) => {
          const { reduceMotion, coarse, narrow, fineWide } = context.conditions ?? {};
          if (reduceMotion) return;

          const reveals = gsap.utils.toArray<HTMLElement>(root.querySelectorAll("[data-reveal]"));
          gsap.set(reveals, { autoAlpha: 0, y: 18 });

          ScrollTrigger.batch(reveals, {
            start: "top 88%",
            once: true,
            onEnter: (batch) => revealBatch(batch),
          });

          const route = root.querySelector<SVGPathElement>("[data-trace-route]");
          const marker = root.querySelector<SVGCircleElement>("[data-trace-marker]");
          const nodes = root.querySelectorAll("[data-trace-node]");
          const metrics = root.querySelectorAll("[data-trace-metric]");
          const heroCopy = root.querySelector<HTMLElement>("[data-hero-copy]");
          const signalMeta = root.querySelectorAll("[data-signal-meta]");

          if (route) gsap.set(route, { strokeDasharray: 1, strokeDashoffset: 1 });
          if (marker) gsap.set(marker, { autoAlpha: 0 });

          const entrance = gsap.timeline({ defaults: { ease: "power2.out" } });
          if (heroCopy) {
            entrance.from(heroCopy, { autoAlpha: 0, y: 16, duration: 0.65 }, 0);
          }
          if (nodes.length) {
            entrance.from(nodes, { autoAlpha: 0, y: 10, duration: 0.5, stagger: 0.1 }, 0.15);
          }
          if (route) {
            entrance.to(route, { strokeDashoffset: 0, duration: 1.1, ease: "power1.inOut" }, 0.25);
          }
          if (marker && route && !coarse && !narrow) {
            entrance.set(marker, { autoAlpha: 1 }, 0.35);
            entrance.to(
              marker,
              {
                duration: 1.1,
                ease: "power1.inOut",
                motionPath: {
                  path: route,
                  align: route,
                  alignOrigin: [0.5, 0.5],
                  autoRotate: false,
                },
              },
              0.35,
            );
            entrance.to(marker, { autoAlpha: 0, duration: 0.25 }, ">-0.05");
          }
          if (metrics.length) {
            entrance.from(metrics, { autoAlpha: 0, y: 8, duration: 0.45, stagger: 0.08 }, 0.85);
          }
          if (signalMeta.length) {
            entrance.from(signalMeta, { autoAlpha: 0, y: 8, duration: 0.45, stagger: 0.06 }, 1);
          }

          const cleanups: Array<() => void> = [];
          if (fineWide) {
            const handshakeTargets = root.querySelectorAll(
              ".trust-fact, .finding-row, .related-finding-button",
            );
            handshakeTargets.forEach((node) => {
              const el = node as HTMLElement;
              const enter = () =>
                gsap.to(el, { y: -2, duration: 0.18, ease: "power1.out", overwrite: "auto" });
              const leave = () =>
                gsap.to(el, { y: 0, duration: 0.22, ease: "power1.out", overwrite: "auto" });
              el.addEventListener("pointerenter", enter);
              el.addEventListener("pointerleave", leave);
              cleanups.push(() => {
                el.removeEventListener("pointerenter", enter);
                el.removeEventListener("pointerleave", leave);
              });
            });
          }

          return () => {
            for (const cleanup of cleanups) cleanup();
          };
        },
      );

      return () => {
        mm.revert();
        ready.current = false;
      };
    },
    { scope, dependencies: [] },
  );

  return null;
}

export default LandingMotion;
