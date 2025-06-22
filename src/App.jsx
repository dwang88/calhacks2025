import React, { useState, useEffect, useRef } from 'react'
import { Loader } from '@googlemaps/js-api-loader'
import { Send, MapPin } from 'lucide-react'
import './App.css'

function App() {
  const [map, setMap] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [mapError, setMapError] = useState('')
  const [isMapLoading, setIsMapLoading] = useState(false)
  const mapRef = useRef(null)
  const messagesEndRef = useRef(null)

  // Google Maps API key for testing
  const API_KEY = 'AIzaSyCHDwwyPsqGFDASunJTyB6Kq1mCi6qQA6U'

  // Sample location data for demonstration
  const locationData = {
    'san francisco': { lat: 37.7749, lng: -122.4194, name: 'San Francisco, CA' },
    'new york': { lat: 40.7128, lng: -74.0060, name: 'New York, NY' },
    'london': { lat: 51.5074, lng: -0.1278, name: 'London, UK' },
    'tokyo': { lat: 35.6762, lng: 139.6503, name: 'Tokyo, Japan' },
    'paris': { lat: 48.8566, lng: 2.3522, name: 'Paris, France' },
    'sydney': { lat: -33.8688, lng: 151.2093, name: 'Sydney, Australia' },
    'dubai': { lat: 25.2048, lng: 55.2708, name: 'Dubai, UAE' },
    'singapore': { lat: 1.3521, lng: 103.8198, name: 'Singapore' },
    'berlin': { lat: 52.5200, lng: 13.4050, name: 'Berlin, Germany' },
    'mumbai': { lat: 19.0760, lng: 72.8777, name: 'Mumbai, India' }
  }

  useEffect(() => {
    // Initialize map immediately with the API key
    initializeMap()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const initializeMap = async () => {
    setIsMapLoading(true)
    setMapError('')

    try {
      const loader = new Loader({
        apiKey: API_KEY,
        version: 'weekly',
        libraries: ['places']
      })

      const google = await loader.load()
      
      if (!mapRef.current) {
        throw new Error('Map container not found')
      }

      const mapInstance = new google.maps.Map(mapRef.current, {
        center: { lat: 37.7749, lng: -122.4194 },
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        mapTypeControl: true,
        streetViewControl: true,
        fullscreenControl: true,
        zoomControl: true,
        gestureHandling: 'cooperative'
      })

      setMap(mapInstance)
      setIsMapLoading(false)
      
      // Add initial welcome message
      if (messages.length === 0) {
        addBotMessage('Hello! I can help you explore locations on the map. Try asking me about cities like San Francisco, New York, London, Tokyo, Paris, Sydney, Dubai, Singapore, Berlin, or Mumbai!')
      }
    } catch (error) {
      console.error('Error loading Google Maps:', error)
      setIsMapLoading(false)
      
      if (error.message.includes('API key')) {
        setMapError('Invalid API key. Please check your Google Maps API key and make sure it has the Maps JavaScript API enabled.')
      } else if (error.message.includes('quota')) {
        setMapError('API quota exceeded. Please check your Google Cloud Console billing and quotas.')
      } else {
        setMapError('Failed to load Google Maps. Please check your internet connection and try again.')
      }
    }
  }

  const addBotMessage = (text) => {
    setMessages(prev => [...prev, { id: Date.now(), text, sender: 'bot' }])
  }

  const addUserMessage = (text) => {
    setMessages(prev => [...prev, { id: Date.now(), text, sender: 'user' }])
  }

  const processMessage = async (message) => {
    setIsLoading(true)
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const lowerMessage = message.toLowerCase()
    let response = ''
    let location = null

    // Check for location queries
    for (const [key, data] of Object.entries(locationData)) {
      if (lowerMessage.includes(key)) {
        location = data
        break
      }
    }

    // Generate response based on message content
    if (location) {
      response = `I found ${location.name}! Let me show you on the map.`
      
      // Pan and zoom to the location
      if (map && window.google) {
        try {
          map.panTo({ lat: location.lat, lng: location.lng })
          map.setZoom(14)
          
          // Add a marker
          new window.google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.name,
            animation: window.google.maps.Animation.DROP
          })
        } catch (error) {
          console.error('Error updating map:', error)
          response = `I found ${location.name}, but there was an issue updating the map. Please try again.`
        }
      }
    } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      response = 'Hello! I can help you explore locations on the map. Try asking me about cities like San Francisco, New York, London, Tokyo, Paris, Sydney, Dubai, Singapore, Berlin, or Mumbai!'
    } else if (lowerMessage.includes('help')) {
      response = 'I can help you find and navigate to different locations. Just ask me about any city or place, and I\'ll show it to you on the map!'
    } else if (lowerMessage.includes('weather') || lowerMessage.includes('temperature')) {
      response = 'I can show you locations on the map, but I don\'t have real-time weather data. Try asking me about specific cities instead!'
    } else if (lowerMessage.includes('restaurant') || lowerMessage.includes('food')) {
      response = 'I can help you find locations, but for restaurant recommendations, you might want to use Google Maps directly or other food apps!'
    } else {
      response = 'I\'m here to help you explore locations on the map! Try asking me about cities like San Francisco, New York, London, Tokyo, Paris, Sydney, Dubai, Singapore, Berlin, or Mumbai.'
    }

    addBotMessage(response)
    setIsLoading(false)
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const message = inputMessage.trim()
    addUserMessage(message)
    setInputMessage('')
    
    await processMessage(message)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }

  return (
    <div className="app">
      <div className="map-container">
        {isMapLoading && (
          <div className="map-loading">
            <div className="spinner"></div>
            <span>Loading map...</span>
          </div>
        )}
        
        {mapError && (
          <div className="map-error">
            <h3>⚠️ Map Error</h3>
            <p>{mapError}</p>
            <button onClick={() => window.location.reload()} className="retry-button">
              Retry
            </button>
          </div>
        )}
        
        <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
        
        {map && (
          <div className="map-overlay">
            <MapPin size={16} />
            <span>Ask me about locations!</span>
          </div>
        )}
      </div>
      
      <div className="chat-container">
        <div className="chat-header">
          <h2>🗺️ Map Assistant</h2>
          <div className="api-key-info">
            <span>🔑 API Key Loaded</span>
          </div>
        </div>
        
        <div className="chat-messages">
          {messages.length === 0 && !mapError && (
            <div className="welcome-message">
              <p>👋 Welcome! I can help you explore locations on the map.</p>
              <p>Try asking me about:</p>
              <ul>
                <li>"Show me San Francisco"</li>
                <li>"Take me to Tokyo"</li>
                <li>"Where is London?"</li>
                <li>"I want to see Paris"</li>
              </ul>
            </div>
          )}
          
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.sender}`}>
              <div className="message-content">
                {message.text}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message bot">
              <div className="message-content">
                <div className="loading">
                  <div className="spinner"></div>
                  Thinking...
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <div className="chat-input">
          <div className="input-container">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about a location..."
              disabled={isLoading || !map}
            />
            <button
              className="send-button"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading || !map}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App 