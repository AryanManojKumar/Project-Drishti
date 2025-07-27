# Drishti Guard - AI-Powered Event Security Platform

A modern, responsive web application built with Next.js and Tailwind CSS for event security management.

## 🚀 Features

- **Landing Page**: Beautiful hero section with call-to-action
- **Role Selection**: Choose between Attendee and Volunteer access
- **Volunteer Dashboard**: Live feed with dispatches and anomaly alerts
- **Attendee SOS**: Emergency assistance with one-click SOS button
- **Command Center**: Administrative access for event management
- **Features Showcase**: Predictive crowd and safety insights

## 🛠 Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful, customizable icons

## 📱 Pages Overview

1. **Homepage** (`/`) - Main landing page with Drishti Guard branding
2. **Role Selection** (`/role-selection`) - Choose between Attendee or Volunteer
3. **Features** (`/features`) - Showcases AI-powered predictive analytics
4. **Volunteer Dashboard** (`/volunteer`) - Live dispatches and alerts
5. **Attendee Dashboard** (`/attendee`) - Emergency SOS functionality
6. **Command Center** (`/command-center`) - Administrative login

## 🎨 Design Features

- **Dark Theme**: Professional navy/slate color scheme
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Interactive Elements**: Hover effects and smooth transitions
- **Modern Layout**: Clean cards, proper spacing, and typography
- **Accessibility**: Semantic HTML and proper contrast ratios

## 🚀 Getting Started

### Prerequisites

Make sure you have Node.js installed on your system.

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
npm run build
npm start
```

## 📁 Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout with navigation
│   ├── page.tsx            # Homepage
│   ├── globals.css         # Global styles
│   ├── role-selection/     # Role selection page
│   ├── features/           # Features showcase
│   ├── volunteer/          # Volunteer dashboard
│   ├── attendee/           # Attendee SOS page
│   └── command-center/     # Command center login
├── components/             # Reusable components (future)
└── lib/                    # Utility functions (future)
```

## 🎯 Key Components

### Navigation
- Consistent header with Drishti branding
- User profile indicators for logged-in states

### SOS System
- Large, prominent emergency button
- Visual feedback and confirmation
- Toast notifications

### Dashboard Cards
- Real-time dispatch information
- Color-coded alert types (Anomaly, SOS, Dispatch)
- Location and timestamp details

### Responsive Grid
- Adaptive layouts for different screen sizes
- Card-based design system

## 🔮 Future Enhancements

- Real-time WebSocket connections
- Interactive maps integration
- Push notifications
- User authentication
- Dashboard analytics
- Mobile app version

## 📄 License

This project is proprietary to Drishti Guard.

---

Built with ❤️ using Next.js and Tailwind CSS
