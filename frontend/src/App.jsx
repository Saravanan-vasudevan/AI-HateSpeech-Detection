import React, { useEffect, useRef, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage'; // Now AuthLoginPage conceptually
import StudentDashboard from './pages/StudentDashboard';
import HateSpeechIdentifier from './pages/HateSpeechIdentifier';
import GamifiedQuiz from './pages/GamifiedQuiz';
import TeacherDashboard from './pages/TeacherDashboard'; // Now Registration Page
import NotFoundPage from './pages/NotFoundPage';
import StudentPointsHistory from './pages/studentpointshistory'; // Student's own history (or specific user's history)
import SplashScreen from './components/SplashScreen';
import TeacherLogin from './pages/TeacherLogin'; // Dedicated Teacher Login
import TeacherMenu from './pages/TeacherMenu'; // Main Teacher Portal
import MultiModelPrediction from './pages/MultiModelPrediction'; // Multi-model comparison page
import RootPage from './pages/RootPage'; // The very first landing page
import TeacherStudentList from './pages/TeacherStudentList'; // Teacher's list of all students
import './App.css';

function App() {
    const canvasRef = useRef(null);
    const [showSplash, setShowSplash] = useState(true);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationFrameId;
        let mouse = { x: null, y: null, radius: 100 };

        const colors = [
            '#FC8337', // Orange
            '#1FBFCF', // Cyan
            '#c2e812'  // Lime Green
        ];

        const setCanvasDimensions = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        window.addEventListener('resize', setCanvasDimensions);
        setCanvasDimensions();

        class Circle {
            constructor(x, y, radius, color, dx, dy) {
                this.x = x;
                this.y = y;
                this.radius = radius;
                this.originalRadius = radius;
                this.targetRadius = radius * 1.5;
                this.color = color;
                this.dx = dx;
                this.dy = dy;
                this.opacity = 0.6;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
                ctx.shadowBlur = 20;
                ctx.shadowColor = `rgba(0, 0, 0, ${this.opacity * 0.8})`;
                ctx.shadowOffsetX = 5;
                ctx.shadowOffsetY = 5;
                const r = parseInt(this.color.slice(1, 3), 16);
                const g = parseInt(this.color.slice(3, 5), 16);
                const b = parseInt(this.color.slice(5, 7), 16);
                ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${this.opacity})`;
                ctx.fill();
                ctx.closePath();
                ctx.shadowBlur = 0;
                ctx.shadowColor = 'transparent';
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 0;
            }

            update() {
                if (this.x + this.radius > canvas.width || this.x - this.radius < 0) {
                    this.dx = -this.dx;
                }
                if (this.y + this.radius > canvas.height || this.y - this.radius < 0) {
                    this.dy = -this.dy;
                }
                this.x += this.dx;
                this.y += this.dy;
                const distance = Math.sqrt(
                    (mouse.x - this.x) * (mouse.x - this.x) +
                    (mouse.y - this.y) * (mouse.y - this.y)
                );
                if (distance < mouse.radius + this.radius) {
                    if (this.radius < this.targetRadius) {
                        this.radius += 1;
                        this.opacity = Math.min(1, this.opacity + 0.02);
                    }
                } else {
                    if (this.radius > this.originalRadius) {
                        this.radius -= 1;
                        this.opacity = Math.max(0.6, this.opacity - 0.02);
                    }
                }
                this.radius = Math.max(this.originalRadius, Math.min(this.targetRadius, this.radius));
                this.opacity = Math.max(0.6, Math.min(1, this.opacity));
                this.draw();
            }
        }

        let circles = [];
        const numberOfCircles = 40;

        const init = () => {
            circles = [];
            for (let i = 0; i < numberOfCircles; i++) {
                const radius = Math.random() * 20 + 10;
                const x = Math.random() * (canvas.width - radius * 2) + radius;
                const y = Math.random() * (canvas.height - radius * 2) + radius;
                const dx = (Math.random() - 0.5) * 1;
                const dy = (Math.random() - 0.5) * 1;
                const color = colors[Math.floor(Math.random() * colors.length)];
                circles.push(new Circle(x, y, radius, color, dx, dy));
            }
        };

        const animate = () => {
            animationFrameId = requestAnimationFrame(animate);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (let i = 0; i < circles.length; i++) {
                circles[i].update();
            }
        };

        const handleMouseMove = (event) => {
            mouse.x = event.clientX;
            mouse.y = event.clientY;
        };

        window.addEventListener('mousemove', handleMouseMove);

        init();
        animate();

        return () => {
            cancelAnimationFrame(animationFrameId);
            window.removeEventListener('resize', setCanvasDimensions);
            window.removeEventListener('mousemove', handleMouseMove);
        };
    }, []);

    const handleSplashFinish = () => {
        setShowSplash(false);
    };

    return (
        <div className="App">
            {showSplash && <SplashScreen onFinish={handleSplashFinish} />}
            <canvas ref={canvasRef} id="globalCanvas" className="global-canvas"></canvas> 

            {!showSplash && (
                <Routes>
                    <Route path="/" element={<RootPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/dashboard" element={<StudentDashboard />} />
                    <Route path="/hate-speech-identifier" element={<HateSpeechIdentifier />} />
                    <Route path="/gamified-quiz" element={<GamifiedQuiz />} />
                    <Route path="/teacher-dashboard" element={<TeacherDashboard />} />
                    <Route path="/teacher-login" element={<TeacherLogin />} />
                    <Route path="/teacher-menu" element={<TeacherMenu />} />
                    <Route path="/teacher-students" element={<TeacherStudentList />} /> {/* Teacher's list of all students */}
                    <Route path="/multi-model-comparison" element={<MultiModelPrediction />} />
                    <Route path="/history" element={<StudentPointsHistory />} /> {/* <--- Student's own history */}
                    <Route path="/history/:username" element={<StudentPointsHistory />} /> {/* <--- NEW ROUTE: Specific user's history for teachers */}
                    <Route path="*" element={<NotFoundPage />} />
                </Routes>
            )}
        </div>
    );
}

export default App;