import React, { useState, useEffect } from 'react';
import { Calendar, Clock, MapPin, Plus, ChevronLeft, ChevronRight } from 'lucide-react';

interface CalendarViewProps {
  user: any;
}

interface Event {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
}

const CalendarView: React.FC<CalendarViewProps> = ({ user }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'day' | 'week' | 'month'>('week');
  const [showAddEvent, setShowAddEvent] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    location: ''
  });

  useEffect(() => {
    fetchEvents();
  }, [user, currentDate]);

  const fetchEvents = async () => {
    try {
      // Mock data for demo
      const mockEvents: Event[] = [
        {
          id: '1',
          title: 'Team Meeting',
          description: 'Weekly team sync',
          start_time: '2024-01-16T09:00:00',
          end_time: '2024-01-16T10:00:00',
          location: 'Conference Room A'
        },
        {
          id: '2',
          title: 'Project Review',
          description: 'Q4 project review meeting',
          start_time: '2024-01-16T14:00:00',
          end_time: '2024-01-16T15:30:00',
          location: 'Virtual'
        },
        {
          id: '3',
          title: 'Client Call',
          description: 'Monthly client check-in',
          start_time: '2024-01-17T11:00:00',
          end_time: '2024-01-17T12:00:00',
          location: 'Phone'
        },
        {
          id: '4',
          title: 'Design Workshop',
          description: 'UX design brainstorming session',
          start_time: '2024-01-18T13:00:00',
          end_time: '2024-01-18T16:00:00',
          location: 'Design Studio'
        },
        {
          id: '5',
          title: 'One-on-One with Sarah',
          description: 'Weekly check-in',
          start_time: '2024-01-19T15:00:00',
          end_time: '2024-01-19T15:30:00',
          location: 'Office'
        }
      ];

      setEvents(mockEvents);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching events:', error);
      setLoading(false);
    }
  };

  const addEvent = async () => {
    if (!newEvent.title.trim() || !newEvent.start_time || !newEvent.end_time) return;

    try {
      const event: Event = {
        id: Date.now().toString(),
        title: newEvent.title,
        description: newEvent.description,
        start_time: newEvent.start_time,
        end_time: newEvent.end_time,
        location: newEvent.location
      };

      setEvents(prev => [...prev, event]);
      setNewEvent({ title: '', description: '', start_time: '', end_time: '', location: '' });
      setShowAddEvent(false);
    } catch (error) {
      console.error('Error adding event:', error);
    }
  };

  const navigateDate = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    
    if (view === 'day') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 1 : -1));
    } else if (view === 'week') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
    } else {
      newDate.setMonth(newDate.getMonth() + (direction === 'next' ? 1 : -1));
    }
    
    setCurrentDate(newDate);
  };

  const getWeekDays = () => {
    const start = new Date(currentDate);
    const day = start.getDay();
    const diff = start.getDate() - day;
    start.setDate(diff);

    const days = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(start);
      date.setDate(start.getDate() + i);
      days.push(date);
    }
    return days;
  };

  const getEventsForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return events.filter(event => 
      event.start_time.startsWith(dateStr)
    );
  };

  const formatTime = (timeStr: string) => {
    return new Date(timeStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDateRange = () => {
    if (view === 'day') {
      return currentDate.toLocaleDateString([], { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    } else if (view === 'week') {
      const weekDays = getWeekDays();
      const start = weekDays[0];
      const end = weekDays[6];
      return `${start.toLocaleDateString([], { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}`;
    } else {
      return currentDate.toLocaleDateString([], { year: 'numeric', month: 'long' });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Calendar</h2>
          <p className="text-gray-600">Manage your schedule with CalendarFlow AI</p>
        </div>
        <button
          onClick={() => setShowAddEvent(true)}
          className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Event
        </button>
      </div>

      {/* Calendar Controls */}
      <div className="flex justify-between items-center bg-white rounded-lg p-4 shadow-sm border border-gray-200">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigateDate('prev')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          
          <h3 className="text-lg font-semibold text-gray-900 min-w-[200px]">
            {formatDateRange()}
          </h3>
          
          <button
            onClick={() => navigateDate('next')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>

        <div className="flex space-x-2">
          {(['day', 'week', 'month'] as const).map((viewType) => (
            <button
              key={viewType}
              onClick={() => setView(viewType)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                view === viewType
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {viewType.charAt(0).toUpperCase() + viewType.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Add Event Modal */}
      {showAddEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Add New Event</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={newEvent.title}
                  onChange={(e) => setNewEvent(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter event title..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newEvent.description}
                  onChange={(e) => setNewEvent(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows={2}
                  placeholder="Enter event description..."
                />
              </div>
              
              <div className="flex space-x-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                  <input
                    type="datetime-local"
                    value={newEvent.start_time}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, start_time: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
                  <input
                    type="datetime-local"
                    value={newEvent.end_time}
                    onChange={(e) => setNewEvent(prev => ({ ...prev, end_time: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input
                  type="text"
                  value={newEvent.location}
                  onChange={(e) => setNewEvent(prev => ({ ...prev, location: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter location..."
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowAddEvent(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={addEvent}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Add Event
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Calendar View */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {view === 'week' && (
          <div className="p-4">
            <div className="grid grid-cols-8 gap-4">
              {/* Time column */}
              <div className="text-sm text-gray-500">
                <div className="h-12"></div>
                {Array.from({ length: 12 }, (_, i) => (
                  <div key={i} className="h-16 border-t border-gray-100 pt-1">
                    {i + 8}:00
                  </div>
                ))}
              </div>
              
              {/* Day columns */}
              {getWeekDays().map((day, dayIndex) => {
                const dayEvents = getEventsForDate(day);
                const isToday = day.toDateString() === new Date().toDateString();
                
                return (
                  <div key={dayIndex} className="min-h-full">
                    <div className={`text-center p-2 rounded-lg mb-2 ${
                      isToday ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700'
                    }`}>
                      <div className="text-xs font-medium">
                        {day.toLocaleDateString([], { weekday: 'short' })}
                      </div>
                      <div className={`text-lg font-semibold ${
                        isToday ? 'text-indigo-700' : 'text-gray-900'
                      }`}>
                        {day.getDate()}
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      {dayEvents.map((event) => (
                        <div
                          key={event.id}
                          className="bg-indigo-100 border-l-4 border-indigo-600 p-2 rounded text-xs"
                        >
                          <div className="font-medium text-indigo-900">{event.title}</div>
                          <div className="text-indigo-700">
                            {formatTime(event.start_time)} - {formatTime(event.end_time)}
                          </div>
                          {event.location && (
                            <div className="text-indigo-600 flex items-center mt-1">
                              <MapPin className="h-3 w-3 mr-1" />
                              {event.location}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {view === 'day' && (
          <div className="p-4">
            <div className="space-y-4">
              {getEventsForDate(currentDate).map((event) => (
                <div
                  key={event.id}
                  className="bg-indigo-50 border border-indigo-200 rounded-lg p-4"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-indigo-900">{event.title}</h4>
                      {event.description && (
                        <p className="text-sm text-indigo-700 mt-1">{event.description}</p>
                      )}
                    </div>
                    <div className="text-sm text-indigo-600">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {formatTime(event.start_time)} - {formatTime(event.end_time)}
                      </div>
                      {event.location && (
                        <div className="flex items-center mt-1">
                          <MapPin className="h-4 w-4 mr-1" />
                          {event.location}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {getEventsForDate(currentDate).length === 0 && (
                <div className="text-center py-8">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No events today</h3>
                  <p className="text-gray-600">You have a free day!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {view === 'month' && (
          <div className="p-4">
            <div className="text-center py-8">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Month View</h3>
              <p className="text-gray-600">Month view coming soon!</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CalendarView;