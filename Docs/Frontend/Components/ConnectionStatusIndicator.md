# Connection Status Indicator Component

## Overview

The `ConnectionStatusIndicator` is a reusable component that displays connection status indicators for various services in the RPGer application. It provides a consistent way to show connection status across different widgets.

## Features

- Displays connection status for backend, MongoDB, Redis, and Chroma services
- Supports different sizes (small, medium, large)
- Can be displayed horizontally or vertically
- Automatically refreshes connection status at configurable intervals
- Color-coded status indicators:
  - Green: Connected
  - Red: Disconnected
  - Amber: Connecting

## Usage

### Basic Usage

```tsx
import ConnectionStatusIndicator from '../common/ConnectionStatusIndicator';

// In your component:
<ConnectionStatusIndicator 
  services={['backend', 'mongodb']} 
  size="small" 
  horizontal={true} 
  refreshInterval={15000}
/>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `services` | `ServiceType[]` | Required | Array of services to display status for. Options: 'backend', 'mongodb', 'redis', 'chroma' |
| `showLabels` | `boolean` | `true` | Whether to show service labels next to indicators |
| `size` | `'small' \| 'medium' \| 'large'` | `'medium'` | Size of the indicators |
| `refreshInterval` | `number` | `30000` | Interval in milliseconds to refresh connection status |
| `horizontal` | `boolean` | `false` | Whether to display indicators horizontally |

### Example: Adding to a Widget Header

```tsx
<WidgetHeader theme={theme}>
  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
    <WidgetTitle theme={theme}>Widget Title</WidgetTitle>
    <ConnectionStatusIndicator 
      services={['backend', 'mongodb']} 
      size="small" 
      horizontal={true} 
      refreshInterval={15000}
    />
  </div>
  <div>
    {/* Other header controls */}
  </div>
</WidgetHeader>
```

## Implementation Details

The component uses the `useSocket` hook to check backend connection status and makes API calls to `/api/status` to check the status of other services. It automatically refreshes the status at the specified interval.

### Connection States

The component displays three possible connection states for each service:
1. **Connected** (green) - The service is running and accessible
2. **Disconnected** (red) - The service is not running or not accessible
3. **Connecting** (amber) - The component is attempting to connect to the service

## Styling

The component uses styled-components for styling and adapts to the current theme. The size of the indicators and labels can be customized using the `size` prop.

## File Location

`/app_stack/frontend/src/components/common/ConnectionStatusIndicator.tsx`

## Dependencies

- React
- styled-components
- SocketContext (for backend connection status)
- API service (for checking other service connections)

## Troubleshooting

If the indicators consistently show disconnected status:

1. Check that the backend server is running
2. Verify that the API endpoint `/api/status` is accessible
3. Check that the services (MongoDB, Redis, Chroma) are running
4. Check browser console for any API errors
