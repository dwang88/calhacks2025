# 🗺️ Maps Chat App

An interactive web application that combines Google Maps with a chat interface, allowing users to ask questions about locations and automatically navigate to them on the map.

## ✨ Features

- **Interactive Google Maps**: Full-featured map with zoom, pan, and street view controls
- **Chat Interface**: Ask questions about locations in natural language
- **Automatic Navigation**: Map automatically zooms and pans to requested locations
- **Location Markers**: Animated markers appear at searched locations
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, intuitive interface with smooth animations

## 🚀 Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn
- Google Maps API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd calhacks2025
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Get a Google Maps API Key**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the **Maps JavaScript API**
   - Create credentials (API key)
   - Copy the API key

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Enter your API key**
   - Open the application in your browser (usually `http://localhost:3000`)
   - Enter your Google Maps API key when prompted
   - The key will be saved in your browser's localStorage

## 🎯 How to Use

1. **Ask about locations**: Type questions like:
   - "Show me San Francisco"
   - "Take me to Tokyo"
   - "Where is London?"
   - "I want to see Paris"

2. **Watch the magic**: The map will automatically:
   - Pan to the requested location
   - Zoom in to show details
   - Drop an animated marker

3. **Explore**: Use the map controls to:
   - Zoom in/out
   - Switch to satellite view
   - Enter street view
   - Fullscreen mode

## 🌍 Supported Locations

The app currently supports these major cities:
- San Francisco, CA
- New York, NY
- London, UK
- Tokyo, Japan
- Paris, France
- Sydney, Australia
- Dubai, UAE
- Singapore
- Berlin, Germany
- Mumbai, India

## 🛠️ Built With

- **React 18** - Frontend framework
- **Vite** - Build tool and dev server
- **Google Maps JavaScript API** - Map functionality
- **Lucide React** - Icons
- **CSS3** - Styling and animations

## 📁 Project Structure

```
calhacks2025/
├── src/
│   ├── App.jsx          # Main application component
│   ├── App.css          # Component-specific styles
│   ├── main.jsx         # React entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
└── README.md           # This file
```

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 🎨 Customization

### Adding New Locations

To add more locations, edit the `locationData` object in `src/App.jsx`:

```javascript
const locationData = {
  'your city': { lat: YOUR_LAT, lng: YOUR_LNG, name: 'Your City, Country' },
  // ... existing locations
}
```

### Styling

- Global styles: `src/index.css`
- Component styles: `src/App.css`
- The app uses CSS custom properties for easy theming

## 🔒 Security Notes

- API keys are stored in browser localStorage
- For production, consider using environment variables
- Restrict your API key to specific domains in Google Cloud Console

## 🚀 Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. Deploy the `dist` folder to your hosting service (Netlify, Vercel, etc.)

3. Set up environment variables for your API key if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Maps API for map functionality
- React team for the amazing framework
- Vite for the fast build tool
- Lucide for the beautiful icons

---

**Happy exploring! 🌍🗺️** 