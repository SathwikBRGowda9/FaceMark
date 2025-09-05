# FaceMark - Face Recognition Attendance System

## Overview

A comprehensive web-based attendance management system branded as "FaceMark" that utilizes face recognition technology for automated student check-ins. The system provides dual-role access for students and administrators, with real-time webcam integration and attendance tracking capabilities. Built with Flask and designed for educational institutions seeking modern attendance solutions.

## Recent Changes (August 2024)

### Brand Identity & Navigation
- **FaceMark Branding**: Complete rebranding with custom SVG logo featuring face recognition theme
- **Enhanced Navigation**: Fixed navigation bar with brand logo and smooth scrolling
- **Contact Integration**: Comprehensive contact section with form, multiple contact methods, and social media links
- **Professional Footer**: Multi-column footer with copyright "© 2024 Satwik. All rights reserved."
- **Social Media Integration**: Animated social media icons for Instagram, GitHub, Facebook, and LinkedIn

### Email Notification System
- **SMTP Integration**: Gmail SMTP server configuration with provided credentials
- **Attendance Confirmations**: Automated email confirmations sent when students mark attendance
- **Absence Alerts**: Automated absence notifications sent to students after configurable cutoff time
- **Admin Controls**: Notification settings management in admin dashboard
- **HTML Email Templates**: Professional email templates with FaceMark branding

### Social Login Integration
- **Google OAuth**: "Continue with Google" button on login pages (placeholder implementation)
- **GitHub OAuth**: "Continue with GitHub" button on login pages (placeholder implementation)
- **Social Provider Support**: Database schema supports multiple authentication providers
- **Fallback Authentication**: Traditional username/password login remains available

### Enhanced User Experience
- **Dark Mode Toggle**: System-wide dark mode with localStorage persistence
- **Mobile Responsiveness**: Optimized layout for all device sizes
- **Loading Animations**: Animated loading screens during authentication and face recognition
- **Enhanced Forms**: Password visibility toggle, improved validation, and better UX
- **Notification Toasts**: Real-time success/error notifications with auto-dismiss

### Technical Improvements
- **Database Migration**: Automated migration script for schema updates
- **Email Service Layer**: Centralized email handling with threading for performance
- **Error Handling**: Comprehensive error logging and user feedback
- **Security Enhancements**: Proper password hashing and session management

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask**: Chosen as the lightweight web framework for rapid development and ease of deployment
- **SQLAlchemy**: Provides ORM capabilities for database operations with declarative models
- **Flask-CORS**: Enables cross-origin requests for face recognition API calls
- **Jinja2 Templates**: Server-side rendering for responsive HTML pages

### Database Design
- **SQLite/PostgreSQL**: Flexible database configuration with environment-based connection strings
- **User Model**: Stores student credentials, face encodings, and profile information
- **Attendance Model**: Records timestamp-based attendance entries with date/time separation
- **UUID Primary Keys**: Ensures unique identification across distributed systems

### Authentication & Authorization
- **Session-based Authentication**: Separate login flows for students and administrators
- **Password Hashing**: Werkzeug security for credential protection
- **Role-based Access**: Student dashboard vs. admin dashboard with different capabilities
- **Hardcoded Admin Credentials**: Simplified admin access as per requirements

### Face Recognition Pipeline
- **OpenCV Integration**: Image processing and computer vision operations
- **Base64 Image Handling**: Web-friendly image data transmission
- **Placeholder Recognition Logic**: Extensible architecture for DeepFace integration
- **Real-time Webcam Processing**: Browser-based camera access with JavaScript

### Frontend Architecture
- **Bootstrap 5**: Responsive design framework for cross-device compatibility
- **Font Awesome**: Icon library for enhanced user interface
- **Custom CSS**: Animated backgrounds and dashboard styling
- **Vanilla JavaScript**: Face detection utilities and dashboard interactions

### Data Management
- **CSV Export**: Attendance data export functionality for reporting
- **Real-time Statistics**: Dashboard metrics with live updates
- **Date-based Filtering**: Flexible attendance record querying

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.1.3**: UI framework via CDN
- **Font Awesome 6.0.0**: Icon library via CDN
- **Face-API.js**: Face detection models (planned integration)

### Python Packages
- **Flask**: Web framework and routing
- **Flask-SQLAlchemy**: Database ORM
- **Flask-CORS**: Cross-origin resource sharing
- **OpenCV (cv2)**: Computer vision and image processing
- **Pillow**: Image manipulation library
- **NumPy**: Numerical computations for image arrays

### Infrastructure
- **Environment Variables**: Configuration for database URLs and session secrets
- **ProxyFix Middleware**: Production deployment compatibility
- **SQLite Default**: Local development database with PostgreSQL production option

### Planned Integrations
- **DeepFace**: Advanced face recognition capabilities
- **External Camera APIs**: Enhanced webcam functionality
- **Cloud Storage**: Photo storage solutions