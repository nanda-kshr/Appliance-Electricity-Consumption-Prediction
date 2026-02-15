"use client";

import React, { useEffect, useState } from 'react';

export default function CircuitBackground() {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) return null;

    return (
        <div className="circuit-bg">
            <svg
                className="circuit-svg"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 1920 1080"
                preserveAspectRatio="xMidYMid slice"
            >
                <defs>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="4" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>

                    <linearGradient id="trace-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="rgba(16, 185, 129, 0)" />
                        <stop offset="50%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="rgba(59, 130, 246, 0)" />
                    </linearGradient>

                    <mask id="circuit-mask">
                        {/* 
               Complex path network representing a circuit.
               M = Move to, L = Line to
               These are decorative lines covering the screen 
            */}

                        {/* Top Left Cluster */}
                        <path className="circuit-path" d="M100 100 L 300 100 L 320 120 L 500 120" />
                        <circle cx="100" cy="100" r="3" fill="white" />
                        <circle cx="500" cy="120" r="3" fill="white" />

                        <path className="circuit-path" d="M150 50 L 150 150 L 170 170 L 400 170" />
                        <circle cx="150" cy="50" r="3" fill="white" />

                        {/* Bottom Right Cluster */}
                        <path className="circuit-path" d="M1800 1000 L 1600 1000 L 1580 980 L 1400 980" />
                        <circle cx="1800" cy="1000" r="3" fill="white" />
                        <circle cx="1400" cy="980" r="3" fill="white" />

                        <path className="circuit-path" d="M1750 1050 L 1750 950 L 1730 930 L 1500 930" />

                        {/* Crossing Lines */}
                        <path className="circuit-path" d="M0 500 L 200 500 L 250 550 L 600 550" />
                        <path className="circuit-path" d="M1920 600 L 1700 600 L 1650 550 L 1300 550" />

                        <path className="circuit-path" d="M600 0 L 600 200 L 650 250 L 650 800" />
                        <path className="circuit-path" d="M1300 1080 L 1300 900 L 1250 850 L 1250 300" />

                        {/* Center decorative */}
                        <path className="circuit-path" d="M800 400 L 960 400 L 960 680 L 1120 680" />
                        <circle cx="800" cy="400" r="3" fill="white" />
                        <circle cx="1120" cy="680" r="3" fill="white" />

                    </mask>
                </defs>

                {/* Base Static Circuit (Darker, always visible) */}
                <g stroke="rgba(59, 130, 246, 0.15)" strokeWidth="2" fill="none">
                    {/* Reusing the paths for the static background */}
                    <path d="M100 100 L 300 100 L 320 120 L 500 120" />
                    <path d="M150 50 L 150 150 L 170 170 L 400 170" />
                    <path d="M1800 1000 L 1600 1000 L 1580 980 L 1400 980" />
                    <path d="M1750 1050 L 1750 950 L 1730 930 L 1500 930" />
                    <path d="M0 500 L 200 500 L 250 550 L 600 550" />
                    <path d="M1920 600 L 1700 600 L 1650 550 L 1300 550" />
                    <path d="M600 0 L 600 200 L 650 250 L 650 800" />
                    <path d="M1300 1080 L 1300 900 L 1250 850 L 1250 300" />
                    <path d="M800 400 L 960 400 L 960 680 L 1120 680" />

                    {/* Nodes */}
                    <circle cx="100" cy="100" r="3" fill="rgba(59, 130, 246, 0.3)" stroke="none" />
                    <circle cx="500" cy="120" r="3" fill="rgba(59, 130, 246, 0.3)" stroke="none" />
                    <circle cx="1800" cy="1000" r="3" fill="rgba(59, 130, 246, 0.3)" stroke="none" />
                    <circle cx="1400" cy="980" r="3" fill="rgba(59, 130, 246, 0.3)" stroke="none" />
                    <circle cx="800" cy="400" r="3" fill="rgba(59, 130, 246, 0.3)" stroke="none" />
                    <circle cx="1120" cy="680" r="3" fill="rgba(59, 130, 246, 0.3)" stroke="none" />
                </g>

                {/* Animated Light Flow */}
                <g stroke="url(#trace-grad)" strokeWidth="3" fill="none" filter="url(#glow)">
                    {/* These paths will have the dash-offset animation */}
                    <path className="animate-flow" d="M100 100 L 300 100 L 320 120 L 500 120" />
                    <path className="animate-flow delay-1" d="M150 50 L 150 150 L 170 170 L 400 170" />
                    <path className="animate-flow delay-2" d="M1800 1000 L 1600 1000 L 1580 980 L 1400 980" />
                    <path className="animate-flow delay-3" d="M1750 1050 L 1750 950 L 1730 930 L 1500 930" />
                    <path className="animate-flow delay-1" d="M0 500 L 200 500 L 250 550 L 600 550" />
                    <path className="animate-flow delay-2" d="M1920 600 L 1700 600 L 1650 550 L 1300 550" />
                    <path className="animate-flow" d="M600 0 L 600 200 L 650 250 L 650 800" />
                    <path className="animate-flow delay-3" d="M1300 1080 L 1300 900 L 1250 850 L 1250 300" />
                    <path className="animate-flow delay-2" d="M800 400 L 960 400 L 960 680 L 1120 680" />
                </g>
            </svg>

            <style jsx>{`
        .circuit-bg {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          z-index: -1;
          background-color: #050a14; /* Deep black/blue bg */
          overflow: hidden;
          pointer-events: none;
        }

        .circuit-svg {
          width: 100%;
          height: 100%;
        }

        .animate-flow {
          stroke-dasharray: 1000;
          stroke-dashoffset: 1000;
          animation: flow 4s linear infinite;
        }
        
        .delay-1 { animation-delay: 1s; }
        .delay-2 { animation-delay: 2s; }
        .delay-3 { animation-delay: 3s; }

        @keyframes flow {
          0% {
            stroke-dashoffset: 1000;
            opacity: 0;
          }
          10% {
             opacity: 1;
          }
          80% {
             opacity: 1;
          }
          100% {
            stroke-dashoffset: -1000;
            opacity: 0;
          }
        }
      `}</style>
        </div>
    );
}
