import React from 'react';

interface Notification {
  message_id: string;
  recipient: string;
  status: string;
  retry_count: number;
}

interface Props {
  notifications: Notification[];
}

const NotificationsTable: React.FC<Props> = ({ notifications }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr>
            <th className="px-6 py-3 border-b border-gray-200 bg-gray-50 text-left text-xs leading-4 font-medium text-gray-500 uppercase tracking-wider">
              Message ID
            </th>
            <th className="px-6 py-3 border-b border-gray-200 bg-gray-50 text-left text-xs leading-4 font-medium text-gray-500 uppercase tracking-wider">
              Recipient
            </th>
            <th className="px-6 py-3 border-b border-gray-200 bg-gray-50 text-left text-xs leading-4 font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 border-b border-gray-200 bg-gray-50 text-left text-xs leading-4 font-medium text-gray-500 uppercase tracking-wider">
              Retries
            </th>
          </tr>
        </thead>
        <tbody>
          {notifications.map((n) => (
            <tr key={n.message_id}>
              <td className="px-6 py-4 whitespace-no-wrap border-b border-gray-200">
                {n.message_id}
              </td>
              <td className="px-6 py-4 whitespace-no-wrap border-b border-gray-200">
                {n.recipient}
              </td>
              <td className="px-6 py-4 whitespace-no-wrap border-b border-gray-200">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    n.status === 'SENT'
                      ? 'bg-green-100 text-green-800'
                      : n.status === 'FAILED'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {n.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-no-wrap border-b border-gray-200">
                {n.retry_count}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default NotificationsTable;
