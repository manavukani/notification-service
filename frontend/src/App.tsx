import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import NotificationsTable from './components/NotificationsTable';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const notificationsRes = await axios.get(`${API_URL}/notifications`);
        setNotifications(notificationsRes.data);

        const statsRes = await axios.get(`${API_URL}/stats`);
        setStats(statsRes.data);
      } catch (error) {
        console.error('Error fetching data', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Notification Delivery Dashboard
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Delivery Throughput</h2>
            <LineChart width={500} height={300} data={stats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="sent" stroke="#82ca9d" />
              <Line type="monotone" dataKey="failed" stroke="#8884d8" />
            </LineChart>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">System Health</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-green-50 rounded">
                <div className="text-sm text-green-600">Success Rate</div>
                <div className="text-2xl font-bold text-green-800">99.2%</div>
              </div>
              <div className="p-4 bg-blue-50 rounded">
                <div className="text-sm text-blue-600">Avg Latency</div>
                <div className="text-2xl font-bold text-blue-800">45ms</div>
              </div>
              <div className="p-4 bg-yellow-50 rounded">
                <div className="text-sm text-yellow-600">DLQ Depth</div>
                <div className="text-2xl font-bold text-yellow-800">12</div>
              </div>
              <div className="p-4 bg-purple-50 rounded">
                <div className="text-sm text-purple-600">Total Processed</div>
                <div className="text-2xl font-bold text-purple-800">15.4k</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">Recent Notifications</h2>
          </div>
          <NotificationsTable notifications={notifications} />
        </div>
      </div>
    </div>
  );
}

export default App;
