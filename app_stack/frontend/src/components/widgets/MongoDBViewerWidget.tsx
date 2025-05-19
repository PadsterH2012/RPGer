import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { useTheme } from '../../context/ThemeContext';
import { WidgetProps } from '../../types/widget';
import api from '../../services/api';
import mockApi from '../../services/mockApi';
import ConnectionStatusIndicator from '../common/ConnectionStatusIndicator';

// Widget container
const MongoDBViewerContainer = styled.div<{ theme: string }>`
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--${props => props.theme}-widget-bg);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
`;

// Widget header
const WidgetHeader = styled.div<{ theme: string }>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--${props => props.theme}-widget-header-bg);
  border-bottom: 1px solid var(--${props => props.theme}-border);
`;

// Widget title
const WidgetTitle = styled.h3<{ theme: string }>`
  margin: 0;
  color: var(--${props => props.theme}-text-primary);
  font-size: var(--font-size-md);
  font-weight: 600;
`;

// Widget content
const WidgetContent = styled.div<{ theme: string }>`
  flex: 1;
  padding: var(--spacing-md);
  overflow-y: auto;
  color: var(--${props => props.theme}-text-primary);
  display: flex;
  flex-direction: column;
`;

// Controls container
const ControlsContainer = styled.div<{ theme: string }>`
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
`;

// Main content container with sidebar and detail view
const MainContentContainer = styled.div<{ theme: string }>`
  display: flex;
  flex: 1;
  gap: var(--spacing-md);
  overflow: hidden;
`;

// Sidebar for listing records
const Sidebar = styled.div<{ theme: string }>`
  width: 200px;
  overflow-y: auto;
  border-right: 1px solid var(--${props => props.theme}-border);
  background-color: var(--${props => props.theme}-sidebar-bg, rgba(0, 0, 0, 0.05));
  border-radius: var(--border-radius-sm);
`;

// Main content area
const MainContent = styled.div<{ theme: string }>`
  flex: 1;
  overflow-y: auto;
  background-color: var(--${props => props.theme}-card-bg);
  border-radius: var(--border-radius-sm);
  position: relative;
`;

// Select dropdown
const Select = styled.select<{ theme: string }>`
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--${props => props.theme}-border);
  background-color: var(--${props => props.theme}-input-bg);
  color: var(--${props => props.theme}-text-primary);
  font-size: var(--font-size-sm);
  min-width: 150px;

  &:focus {
    outline: none;
    border-color: var(--${props => props.theme}-primary);
  }
`;

// Button
const Button = styled.button<{ theme: string }>`
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--${props => props.theme}-border);
  background-color: var(--${props => props.theme}-button-bg);
  color: var(--${props => props.theme}-text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;

  &:hover {
    background-color: var(--${props => props.theme}-button-hover-bg);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

// Search input
const SearchInput = styled.input<{ theme: string }>`
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--${props => props.theme}-border);
  background-color: var(--${props => props.theme}-input-bg);
  color: var(--${props => props.theme}-text-primary);
  font-size: var(--font-size-sm);
  flex: 1;
  min-width: 200px;

  &:focus {
    outline: none;
    border-color: var(--${props => props.theme}-primary);
  }
`;

// Record list container
const RecordListContainer = styled.div<{ theme: string }>`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs);
  height: 100%;
`;

// Record list item
const RecordListItem = styled.div<{ theme: string, isSelected: boolean }>`
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  background-color: ${props => props.isSelected
    ? `var(--${props.theme}-selection-bg)`
    : 'transparent'};
  cursor: pointer;
  font-size: var(--font-size-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  &:hover {
    background-color: ${props => props.isSelected
      ? `var(--${props.theme}-selection-bg)`
      : `var(--${props.theme}-card-hover-bg, rgba(0, 0, 0, 0.05))`};
  }
`;

// Record name
const RecordName = styled.div<{ theme: string }>`
  font-weight: 500;
  color: var(--${props => props.theme}-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

// Record category
const RecordCategory = styled.div<{ theme: string }>`
  font-size: var(--font-size-xs);
  color: var(--${props => props.theme}-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

// Detail view
const DetailView = styled.div<{ theme: string }>`
  padding: var(--spacing-md);
  height: 100%;
  overflow-y: auto;
`;

// Format toggle container
const FormatToggleContainer = styled.div<{ theme: string }>`
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
  padding: 5px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
`;

// Format toggle button
const FormatToggleButton = styled.button<{ theme: string, isActive: boolean }>`
  padding: 8px 12px;
  background-color: ${props => props.isActive
    ? `#8a2be2` // More vibrant purple
    : `#e0e0e0`}; // Light gray
  color: ${props => props.isActive
    ? 'white'
    : `#333`}; // Dark text for contrast
  border: 2px solid ${props => props.isActive
    ? `#6a1cb7` // Darker purple border
    : `#ccc`}; // Light gray border
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600; // Bold text
  cursor: pointer;
  transition: all 0.2s ease-in-out; // Smooth transition
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); // More visible shadow
  z-index: 100; // Ensure it's above other elements

  &:hover {
    background-color: ${props => props.isActive
      ? `#7c1cd6` // Slightly darker purple on hover
      : `#d0d0d0`}; // Slightly darker gray on hover
    transform: translateY(-1px); // Slight lift effect
    box-shadow: 0 3px 5px rgba(0, 0, 0, 0.25); // Enhanced shadow on hover
  }

  &:active {
    transform: translateY(1px); // Press effect
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2); // Reduced shadow when pressed
  }
`;

// Standard format view
const StandardFormatView = styled.div<{ theme: string }>`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
`;

// Standard format section
const StandardFormatSection = styled.div<{ theme: string }>`
  margin-bottom: var(--spacing-md);
`;

// Standard format section title
const StandardFormatSectionTitle = styled.h4<{ theme: string }>`
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--${props => props.theme}-text-primary);
  font-size: var(--font-size-sm);
  font-weight: 600;
  border-bottom: 1px solid var(--${props => props.theme}-border);
  padding-bottom: var(--spacing-xs);
`;

// Standard format section content
const StandardFormatSectionContent = styled.div<{ theme: string }>`
  color: var(--${props => props.theme}-text-primary);
  font-size: var(--font-size-sm);
`;

// JSON format view
const JsonFormatView = styled.div<{ theme: string }>`
  margin: 0;
  padding: var(--spacing-md);
  background-color: #1e1e1e; /* Dark background for better contrast */
  border-radius: var(--border-radius-sm);
  overflow: auto;
  max-height: 100%;
  width: 100%;
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
  border: 1px solid #333;
`;

// Status message
const StatusMessage = styled.div<{ theme: string, isError?: boolean }>`
  padding: var(--spacing-md);
  text-align: center;
  color: ${props => props.isError
    ? `var(--${props.theme}-error)`
    : `var(--${props.theme}-text-secondary)`};
`;

// Pagination container
const PaginationContainer = styled.div<{ theme: string }>`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
`;

// Page info
const PageInfo = styled.div<{ theme: string }>`
  color: var(--${props => props.theme}-text-secondary);
  font-size: var(--font-size-sm);
`;

// MongoDB Viewer Widget
const MongoDBViewerWidget: React.FC<WidgetProps> = ({ id, config = {} }) => {
  const { theme } = useTheme();
  const [collections, setCollections] = useState<string[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<string>('monsters');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [results, setResults] = useState<any[]>([]);
  const [filteredResults, setFilteredResults] = useState<any[]>([]);
  const [selectedItem, setSelectedItem] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [viewFormat, setViewFormat] = useState<'standard' | 'json'>('standard');
  const itemsPerPage = 50; // Increased to show more items in the sidebar

  const [isConnected, setIsConnected] = useState<boolean>(false);

  // Fetch collections on mount
  useEffect(() => {
    console.log('MongoDBViewerWidget mounted, fetching collections...');
    fetchCollections();
  }, []);

  // Set default collection when collections change
  useEffect(() => {
    if (collections.length > 0 && !selectedCollection) {
      console.log('Setting default collection from available collections:', collections);
      // Prefer 'monsters' collection if available
      if (collections.includes('monsters')) {
        console.log('Setting default collection to monsters');
        setSelectedCollection('monsters');
      } else {
        console.log('Setting default collection to first available:', collections[0]);
        setSelectedCollection(collections[0]);
      }
    }
  }, [collections, selectedCollection]);

  // Fetch results when collection changes
  useEffect(() => {
    if (selectedCollection) {
      console.log(`Selected collection changed to ${selectedCollection}, fetching results...`);
      fetchResults();
    }
  }, [selectedCollection]);

  // Fetch results when collection or page changes
  useEffect(() => {
    if (selectedCollection) {
      console.log(`Collection or page changed: ${selectedCollection}, page ${page}`);
      fetchResults();
    }
  }, [selectedCollection, page]);

  // Debug log when results change
  useEffect(() => {
    console.log(`Results updated: ${results.length} items, filtered to ${filteredResults.length} items`);
    if (results.length > 0) {
      console.log('First result:', results[0]);
    }
  }, [results, filteredResults]);

  // Auto-select first item when results change
  useEffect(() => {
    if (filteredResults.length > 0 && !selectedItem) {
      setSelectedItem(filteredResults[0]);
    }
  }, [filteredResults]);

  // Log when viewFormat changes
  useEffect(() => {
    console.log('View format changed to:', viewFormat);
  }, [viewFormat]);

  // Fetch collections when component mounts
  useEffect(() => {
    console.log('MongoDB Viewer widget mounted, fetching collections...');
    fetchCollections();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Filter results when search query changes
  useEffect(() => {
    console.log('Search filter effect running. Results length:', results.length);

    if (results.length > 0) {
      if (!searchQuery) {
        console.log('No search query, showing all results:', results.length);
        setFilteredResults(results);
        return;
      }

      console.log('Filtering with query:', searchQuery);
      const lowercaseQuery = searchQuery.toLowerCase();
      const filtered = results.filter(item => {
        // Search in name/title
        const name = (item.name || item.title || '').toLowerCase();
        if (name.includes(lowercaseQuery)) return true;

        // Search in description
        const description = (item.description || '').toLowerCase();
        if (description.includes(lowercaseQuery)) return true;

        // Search in category/type
        const category = (item.category || item.type || '').toLowerCase();
        if (category.includes(lowercaseQuery)) return true;

        return false;
      });

      console.log(`Filtered from ${results.length} to ${filtered.length} items`);
      setFilteredResults(filtered);
    } else {
      console.log('No results to filter, filtered results will be empty');
    }
  }, [results, searchQuery]);

  // Fetch MongoDB collections
  const fetchCollections = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching collections...');

      // Try to fetch from real API first using direct fetch with improved error handling
      try {
        // First try the status endpoint which has collection names
        const apiUrl = 'http://localhost:5002/api/status';
        console.log('Requesting API status from:', apiUrl);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

        const statusResponse = await fetch(apiUrl, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
          },
          credentials: 'omit',
          mode: 'cors',
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (statusResponse.status === 200) {
          const data = await statusResponse.json();
          console.log('Status response:', data);

          // Check if MongoDB is connected - use the explicit connected flag
          const isConnected = data?.mongodb?.connected === true;

          // Log detailed MongoDB status
          console.log('MongoDBViewerWidget: MongoDB status details:', {
            connected: isConnected,
            collections: data?.mongodb?.collections || 0,
            databaseName: data?.mongodb?.databaseName || '',
            collectionNames: data?.mongodb?.collectionNames || []
          });

          // Set connection status based on the connected flag only for consistency
          setIsConnected(isConnected);

          if (!isConnected) {
            console.warn('MongoDB is not connected according to status response');
            setError('MongoDB is not connected. Please check your database connection.');
            throw new Error('MongoDB is not connected');
          }

          // Check if we have collection names in the status response
          if (data?.mongodb?.collectionNames) {
            console.log('Found collections in status response:', data.mongodb.collectionNames);
            setCollections(data.mongodb.collectionNames);

            // If we have a monsterCount, log it
            if (data?.mongodb?.monsterCount) {
              console.log(`MongoDB has ${data.mongodb.monsterCount} monsters`);
            }
            return;
          } else {
            // If we don't have collection names in the status response, try to get them from the database
            console.log('No collection names in status response, trying to get them from the database');
            try {
              const db = data?.mongodb?.databaseName || 'rpger';
              console.log(`Database name: ${db}`);

              // If we have collections count, use that
              if (data?.mongodb?.collections) {
                console.log(`MongoDB has ${data?.mongodb?.collections} collections`);
                // Use default collections as fallback
                setCollections(['monsters', 'spells', 'items', 'npcs', 'characters']);
                return;
              }
            } catch (err) {
              console.error('Error parsing database info:', err);
            }
          }
        } else {
          console.error(`Status API returned status ${statusResponse.status}`);
          throw new Error(`Status API returned status ${statusResponse.status}`);
        }

        // If status endpoint doesn't have collection names, try the collections endpoint
        const collectionsUrl = 'http://localhost:5002/api/collections/';
        console.log('Requesting collections from:', collectionsUrl);

        const collectionsController = new AbortController();
        const collectionsTimeoutId = setTimeout(() => collectionsController.abort(), 5000);

        const collectionsResponse = await fetch(collectionsUrl, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
          },
          credentials: 'omit',
          mode: 'cors',
          signal: collectionsController.signal
        });

        clearTimeout(collectionsTimeoutId);

        if (collectionsResponse.status === 200) {
          const data = await collectionsResponse.json();
          console.log('Collections response:', data);

          if (data?.collections) {
            console.log('Found collections in collections response:', data.collections);
            setCollections(data.collections);
            return;
          }
        }
      } catch (apiErr: any) {
        console.error('Error fetching from real API:', apiErr);
        const errorMessage = apiErr.message || 'Unknown error';
        console.error('Error details:', errorMessage);
        setError(`Failed to connect to MongoDB: ${errorMessage}`);
        // Continue to fallback options
      }

      // Fallback to mock API if real API fails
      try {
        console.log('Falling back to mock API...');
        const mockResponse = await mockApi.getCollections();
        console.log('Mock response:', mockResponse.data);

        if (mockResponse.data?.collections) {
          console.log('Found collections in mock response:', mockResponse.data.collections);
          setCollections(mockResponse.data.collections);
          return;
        }
      } catch (mockErr) {
        console.error('Error fetching from mock API:', mockErr);
        // Continue to default fallback
      }

      // Final fallback to default collections
      console.log('Using default collections fallback');
      setCollections(['monsters', 'spells', 'items', 'npcs', 'characters']);
    } catch (err) {
      console.error('Error fetching collections:', err);
      setError('Failed to fetch collections');
      // Fallback to default collections
      setCollections(['monsters', 'spells', 'items', 'npcs', 'characters']);
    } finally {
      setLoading(false);
    }
  };

  // Fetch results from selected collection
  const fetchResults = async () => {
    try {
      if (!selectedCollection) {
        console.error('No collection selected');
        return;
      }

      setLoading(true);
      setError(null);
      setSelectedItem(null);
      console.log(`Fetching ${selectedCollection} collection data...`);

      // Try to fetch from real API first using direct fetch
      try {
        // First check if MongoDB is connected via status endpoint
        try {
          const statusUrl = 'http://localhost:5002/api/status';
          console.log('Checking MongoDB status from:', statusUrl);

          const statusController = new AbortController();
          const statusTimeoutId = setTimeout(() => statusController.abort(), 5000);

          const statusResponse = await fetch(statusUrl, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Cache-Control': 'no-cache'
            },
            credentials: 'omit',
            mode: 'cors',
            signal: statusController.signal
          });

          clearTimeout(statusTimeoutId);

          if (statusResponse.status === 200) {
            const statusData = await statusResponse.json();
            // Check if MongoDB is connected - use the explicit connected flag
            const isConnected = statusData?.mongodb?.connected === true;

            // Log detailed MongoDB status
            console.log('MongoDBViewerWidget: MongoDB status details (fetchResults):', {
              connected: isConnected,
              collections: statusData?.mongodb?.collections || 0,
              databaseName: statusData?.mongodb?.databaseName || '',
              collectionNames: statusData?.mongodb?.collectionNames || []
            });

            // Set connection status based on the connected flag only for consistency
            setIsConnected(isConnected);

            if (!isConnected) {
              console.warn('MongoDB is not connected according to status response');
              setError('MongoDB is not connected. Please check your database connection.');
              throw new Error('MongoDB is not connected');
            }
            
            // If we got this far, MongoDB is connected. Let's check for collections.
            if (statusData?.mongodb?.collectionNames && 
                statusData.mongodb.collectionNames.length > 0 && 
                !statusData.mongodb.collectionNames.includes(selectedCollection)) {
              console.warn(`Selected collection "${selectedCollection}" does not exist in MongoDB`);
              setError(`Collection "${selectedCollection}" does not exist in MongoDB. Available collections: ${statusData.mongodb.collectionNames.join(', ')}`);
              throw new Error(`Collection "${selectedCollection}" does not exist`);
            }
          }
        } catch (statusErr) {
          console.error('Error checking MongoDB status:', statusErr);
          // Continue anyway to try the collection endpoint
        }

        // Build URL with query parameters
        const url = new URL(`http://localhost:5002/api/collections/${selectedCollection}`);
        url.searchParams.append('page', page.toString());
        url.searchParams.append('limit', itemsPerPage.toString());

        console.log(`Requesting: ${url.toString()}`);

        const collectionController = new AbortController();
        const collectionTimeoutId = setTimeout(() => collectionController.abort(), 8000); // Longer timeout for collection data

        const response = await fetch(url.toString(), {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
          },
          credentials: 'omit',
          mode: 'cors',
          signal: collectionController.signal
        });

        clearTimeout(collectionTimeoutId);
        console.log(`Response status: ${response.status}`);

        if (response.status === 200) {
          const data = await response.json();
          console.log(`Response for ${selectedCollection}:`, data);

          // Check if the response has items property (paginated response)
          const items = data.items || [];

          console.log(`Response data structure:`, JSON.stringify(data).substring(0, 500) + '...');

          if (items.length > 0) {
            console.log(`Found ${items.length} items in ${selectedCollection}`);
            console.log('Sample item structure:', JSON.stringify(items[0]).substring(0, 200) + '...');
            console.log('First item name:', items[0].name || items[0].title || items[0]._id);

            setResults(items);
            setFilteredResults(items); // Initialize filtered results with all results
            setTotalItems(data.total || items.length || 0);
            setTotalPages(Math.ceil((data.total || items.length || 0) / itemsPerPage));

            // Auto-select first item if available
            console.log('Auto-selecting first item:', items[0].name || items[0]._id);
            setSelectedItem(items[0]);
          } else {
            console.log('No items found in collection');
            setResults([]);
            setFilteredResults([]);
            setTotalItems(0);
            setTotalPages(0);
          }
          return;
        } else if (response.status === 404) {
          // Collection not found
          console.warn(`Collection ${selectedCollection} not found`);
          setError(`Collection "${selectedCollection}" not found in the database.`);
          setResults([]);
          setFilteredResults([]);
          setTotalItems(0);
          setTotalPages(0);
          return;
        }
      } catch (apiErr: any) {
        console.error(`Error fetching ${selectedCollection} from real API:`, apiErr);
        const errorMessage = apiErr.message || 'Unknown error';
        console.error('Error details:', errorMessage);
        setError(`Failed to fetch ${selectedCollection}: ${errorMessage}`);
        // Continue to fallback options
      }

      // Fallback to mock API if real API fails
      try {
        console.log(`Falling back to mock API for ${selectedCollection}...`);
        const mockResponse = await mockApi.getCollectionItems(selectedCollection, page, itemsPerPage);
        console.log(`Mock response for ${selectedCollection}:`, mockResponse.data);

        if (mockResponse.data) {
          const items = mockResponse.data.items || [];
          console.log(`Found ${items.length} mock items in ${selectedCollection}`);

          if (items.length > 0) {
            console.log('Using mock data as fallback');
            console.log('Sample mock item:', JSON.stringify(items[0]).substring(0, 200) + '...');

            setResults(items);
            setFilteredResults(items);
            setTotalItems(mockResponse.data.total || items.length || 0);
            setTotalPages(Math.ceil((mockResponse.data.total || items.length || 0) / itemsPerPage));

            // Auto-select first item if available
            console.log('Auto-selecting first mock item:', items[0].name || items[0]._id);
            setSelectedItem(items[0]);
          } else {
            console.log('No mock items found for collection');
            setResults([]);
            setFilteredResults([]);
            setTotalItems(0);
            setTotalPages(0);
          }
          return;
        }
      } catch (mockErr: any) {
        console.error(`Error fetching ${selectedCollection} from mock API:`, mockErr);
        const errorMessage = mockErr.message || 'Unknown error';
        console.error('Mock API error details:', errorMessage);
        // Continue to error handling
      }

      // If we get here, both APIs failed
      throw new Error(`Failed to fetch ${selectedCollection} from any source`);
    } catch (err: any) {
      console.error(`Error fetching ${selectedCollection}:`, err);
      const errorMessage = err.message || 'Unknown error';
      setError(`Failed to fetch ${selectedCollection}: ${errorMessage}`);
      setResults([]);
      setFilteredResults([]);

      // Show a more user-friendly message if we're using mock data
      console.log('Using mock data as fallback due to error');
    } finally {
      setLoading(false);
    }
  };

  // Handle collection change
  const handleCollectionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newCollection = e.target.value;
    console.log(`Collection changed from ${selectedCollection} to ${newCollection}`);
    setSelectedCollection(newCollection);
    setPage(1);
    setSearchQuery('');
  };

  // Handle search input change - now acts as a filter
  const handleSearchInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  // Check connection status in detail - helps with troubleshooting
  const checkConnectionStatus = async () => {
    try {
      setLoading(true);
      const statusUrl = 'http://localhost:5002/api/status';
      
      console.log('Checking connection status in detail...');

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      try {
        const response = await fetch(statusUrl, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
          },
          credentials: 'omit',
          mode: 'cors',
          signal: controller.signal
        });

        clearTimeout(timeoutId);
        
        if (response.status === 200) {
          const data = await response.json();
          const mongoStatus = data?.mongodb || {};
          
          // First check if backend is accessible
          const backendConnected = true; // If we got here, backend is working
          
          // Then check MongoDB connection
          const mongoConnected = mongoStatus.connected === true;
          setIsConnected(mongoConnected);
          
          // Build a detailed status message
          const statusDetails = [
            `Backend API: ${backendConnected ? 'Connected ✅' : 'Disconnected ❌'}`,
            `MongoDB: ${mongoConnected ? 'Connected ✅' : 'Disconnected ❌'}`
          ];
          
          if (mongoConnected) {
            statusDetails.push(`Database: ${mongoStatus.databaseName || 'rpger'}`);
            statusDetails.push(`Collections: ${mongoStatus.collections || 0}`);
            statusDetails.push(`Collection Names: ${(mongoStatus.collectionNames || []).join(', ') || 'None'}`);
          }
          
          // Show the detailed status message
          alert('Connection Status:\n\n' + statusDetails.join('\n'));
          
          // If MongoDB is not connected, show detailed error
          if (!mongoConnected) {
            setError('MongoDB is not connected. Please check your database connection and ensure the MongoDB container is running.');
          } else {
            // Connection successful, clear any error and refresh collections
            setError(null);
            fetchCollections();
          }
        } else {
          throw new Error(`API status endpoint returned ${response.status}`);
        }
      } catch (error) {
        console.error('Error checking connection status:', error);
        setError(`Backend API not accessible at ${statusUrl}. Please check that the backend is running.`);
        alert(`Connection Error: Backend API not accessible at ${statusUrl}.\n\nPlease check that the backend is running and accessible.`);
        setIsConnected(false);
      }
    } finally {
      setLoading(false);
    }
  };

  // Toggle view format between standard and JSON
  const toggleViewFormat = () => {
    console.log('Current format:', viewFormat);
    // Force a direct state change instead of using a callback
    const newFormat = viewFormat === 'standard' ? 'json' : 'standard';
    console.log(`Switching to ${newFormat} format`);
    setViewFormat(newFormat);
  };

  // Handle item selection
  const handleItemSelect = (item: any) => {
    setSelectedItem(item);
  };

  // Handle pagination
  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  // Render standard format value
  const renderStandardValue = (value: any): React.ReactNode => {
    if (value === null || value === undefined) {
      return <em>null</em>;
    }

    if (typeof value === 'object') {
      if (Array.isArray(value)) {
        if (value.length === 0) {
          return <em>(empty array)</em>;
        }
        return (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {value.map((item, index) => (
              <li key={index}>{renderStandardValue(item)}</li>
            ))}
          </ul>
        );
      }

      if (Object.keys(value).length === 0) {
        return <em>(empty object)</em>;
      }

      return (
        <div style={{ marginLeft: 10 }}>
          {Object.entries(value).map(([key, val]) => (
            <div key={key}>
              <strong>{key}:</strong> {renderStandardValue(val)}
            </div>
          ))}
        </div>
      );
    }

    return String(value);
  };

  // Render standard format view
  const renderStandardFormat = () => {
    if (!selectedItem) return null;

    // Group fields into categories
    const basicInfo = ['_id', 'name', 'title', 'category', 'type', 'description'];
    const statsInfo = ['stats', 'metadata', 'abilities'];
    const environmentInfo = ['habitat', 'ecology'];
    const gameInfo = ['campaign_usage', 'encounter_suggestions', 'related_monsters'];
    const otherInfo = Object.keys(selectedItem).filter(key =>
      !basicInfo.includes(key) &&
      !statsInfo.includes(key) &&
      !environmentInfo.includes(key) &&
      !gameInfo.includes(key)
    );

    return (
      <StandardFormatView theme={theme}>
        {/* Basic Information */}
        <StandardFormatSection theme={theme}>
          <StandardFormatSectionTitle theme={theme}>
            Basic Information
          </StandardFormatSectionTitle>
          <StandardFormatSectionContent theme={theme}>
            {basicInfo.map(key => selectedItem[key] !== undefined && (
              <div key={key}>
                <strong>{key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}:</strong>{' '}
                {typeof selectedItem[key] === 'string'
                  ? selectedItem[key]
                  : renderStandardValue(selectedItem[key])}
              </div>
            ))}
          </StandardFormatSectionContent>
        </StandardFormatSection>

        {/* Stats Information */}
        {statsInfo.some(key => selectedItem[key] !== undefined) && (
          <StandardFormatSection theme={theme}>
            <StandardFormatSectionTitle theme={theme}>
              Stats & Abilities
            </StandardFormatSectionTitle>
            <StandardFormatSectionContent theme={theme}>
              {statsInfo.map(key => selectedItem[key] !== undefined && (
                <div key={key}>
                  <strong>{key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}:</strong>{' '}
                  {renderStandardValue(selectedItem[key])}
                </div>
              ))}
            </StandardFormatSectionContent>
          </StandardFormatSection>
        )}

        {/* Environment Information */}
        {environmentInfo.some(key => selectedItem[key] !== undefined) && (
          <StandardFormatSection theme={theme}>
            <StandardFormatSectionTitle theme={theme}>
              Environment & Ecology
            </StandardFormatSectionTitle>
            <StandardFormatSectionContent theme={theme}>
              {environmentInfo.map(key => selectedItem[key] !== undefined && (
                <div key={key}>
                  <strong>{key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}:</strong>{' '}
                  {renderStandardValue(selectedItem[key])}
                </div>
              ))}
            </StandardFormatSectionContent>
          </StandardFormatSection>
        )}

        {/* Game Information */}
        {gameInfo.some(key => selectedItem[key] !== undefined) && (
          <StandardFormatSection theme={theme}>
            <StandardFormatSectionTitle theme={theme}>
              Game Usage
            </StandardFormatSectionTitle>
            <StandardFormatSectionContent theme={theme}>
              {gameInfo.map(key => selectedItem[key] !== undefined && (
                <div key={key}>
                  <strong>{key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}:</strong>{' '}
                  {renderStandardValue(selectedItem[key])}
                </div>
              ))}
            </StandardFormatSectionContent>
          </StandardFormatSection>
        )}

        {/* Other Information */}
        {otherInfo.length > 0 && (
          <StandardFormatSection theme={theme}>
            <StandardFormatSectionTitle theme={theme}>
              Other Information
            </StandardFormatSectionTitle>
            <StandardFormatSectionContent theme={theme}>
              {otherInfo.map(key => selectedItem[key] !== undefined && (
                <div key={key}>
                  <strong>{key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}:</strong>{' '}
                  {renderStandardValue(selectedItem[key])}
                </div>
              ))}
            </StandardFormatSectionContent>
          </StandardFormatSection>
        )}
      </StandardFormatView>
    );
  };

  // Render JSON format view
  const renderJsonFormat = () => {
    if (!selectedItem) return null;

    // Format the JSON with proper indentation
    const formattedJson = JSON.stringify(selectedItem, null, 2);
    console.log('Rendering JSON format:', formattedJson.substring(0, 100) + '...');

    return (
      <JsonFormatView theme={theme}>
        <pre style={{
          margin: 0,
          padding: 0,
          fontFamily: 'Consolas, Monaco, "Courier New", monospace',
          fontSize: '14px',
          lineHeight: '1.5',
          color: '#d4d4d4',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }}>
          {formattedJson}
        </pre>
      </JsonFormatView>
    );
  };

  return (
    <MongoDBViewerContainer theme={theme}>
      <WidgetHeader theme={theme}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <WidgetTitle theme={theme}>MongoDB Viewer</WidgetTitle>
          <ConnectionStatusIndicator
            services={['backend', 'mongodb']}
            size="small"
            horizontal={true}
            refreshInterval={5000}
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {loading && (
            <div style={{
              width: '16px',
              height: '16px',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              borderTop: '2px solid #8a2be2',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
          )}
          <button
            onClick={() => {
              console.log('Refresh button clicked - using direct fetch approach');
              fetchCollections();
              if (selectedCollection) {
                fetchResults();
              }
            }}
            style={{
              padding: '6px 12px',
              backgroundColor: '#8a2be2',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}
            title="Refresh data from MongoDB"
            disabled={loading}
          >
            <span>↻</span> Refresh
          </button>
          <button
            onClick={checkConnectionStatus}
            style={{
              padding: '6px 12px',
              backgroundColor: '#4a5568',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}
            title="Check connection status and diagnose issues"
            disabled={loading}
          >
            <span>🔍</span> Diagnose
          </button>
        </div>
      </WidgetHeader>

      <WidgetContent theme={theme}>
        <ControlsContainer theme={theme}>
          <Select
            theme={theme}
            value={selectedCollection}
            onChange={handleCollectionChange}
          >
            {console.log('Rendering collection options:', collections)}
            {collections.length === 0 ? (
              <option value="">No collections found</option>
            ) : (
              collections.map(collection => (
                <option key={collection} value={collection}>
                  {collection}
                </option>
              ))
            )}
          </Select>

          <SearchInput
            theme={theme}
            placeholder={`Filter ${selectedCollection}...`}
            value={searchQuery}
            onChange={handleSearchInputChange}
          />
        </ControlsContainer>

        {loading ? (
          <StatusMessage theme={theme}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
              <div style={{
                width: '20px',
                height: '20px',
                border: '3px solid rgba(255, 255, 255, 0.3)',
                borderTop: '3px solid #8a2be2',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <span>Loading data from MongoDB...</span>
            </div>
            <style>
              {`
                @keyframes spin {
                  0% { transform: rotate(0deg); }
                  100% { transform: rotate(360deg); }
                }
              `}
            </style>
          </StatusMessage>
        ) : error ? (
          <StatusMessage theme={theme} isError>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
              <div>{error}</div>
              <div style={{ fontSize: '0.9em', marginTop: '10px' }}>
                {isConnected ? 
                  "Connected to MongoDB, but unable to fetch data. The collection may be empty or inaccessible." : 
                  "Unable to connect to MongoDB. The database service may be unavailable."}
              </div>
              <div style={{ fontSize: '0.8em', marginTop: '5px', color: '#666' }}>
                <ul style={{ textAlign: 'left', margin: '5px 0', paddingLeft: '20px' }}>
                  <li>Check that the MongoDB container is running: <code>docker ps | grep rpger-mongodb</code></li>
                  <li>Verify backend is running and can connect to MongoDB</li>
                  <li>Check backend logs for connection errors</li>
                  <li>Try refreshing the page or restarting the application stack</li>
                </ul>
              </div>
              <button 
                onClick={() => {
                  console.log('Retry button clicked');
                  fetchCollections();
                  if (selectedCollection) {
                    fetchResults();
                  }
                }}
                style={{
                  marginTop: '10px',
                  padding: '8px 16px',
                  backgroundColor: '#8a2be2',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Retry Connection
              </button>
            </div>
          </StatusMessage>
        ) : results.length === 0 ? (
          <StatusMessage theme={theme}>
            {selectedCollection ?
              `No records found in the "${selectedCollection}" collection. Try selecting a different collection.` :
              'No collection selected. Please select a collection from the dropdown.'}
          </StatusMessage>
        ) : (
          <MainContentContainer theme={theme}>
            {/* Sidebar with record list */}
            <Sidebar theme={theme}>
              <RecordListContainer theme={theme}>
                {console.log('Rendering sidebar with filteredResults:', filteredResults.length, 'items')}
                {filteredResults.length === 0 ? (
                  <>
                    {console.log('No filtered results to display')}
                    <StatusMessage theme={theme}>No matching records</StatusMessage>
                  </>
                ) : (
                  <>
                    {console.log('Mapping filtered results to RecordListItems')}
                    {filteredResults.map(item => {
                      console.log('Rendering item:', item.name || item.title || item._id);
                      return (
                        <RecordListItem
                          key={item._id}
                          theme={theme}
                          isSelected={selectedItem?._id === item._id}
                          onClick={() => handleItemSelect(item)}
                        >
                          <RecordName theme={theme}>
                            {item.name || item.title || item._id}
                          </RecordName>
                          {(item.category || item.type) && (
                            <RecordCategory theme={theme}>
                              {item.category || item.type}
                            </RecordCategory>
                          )}
                        </RecordListItem>
                      );
                    })}
                  </>
                )}
              </RecordListContainer>

              {totalPages > 1 && (
                <PaginationContainer theme={theme}>
                  <Button
                    theme={theme}
                    onClick={() => handlePageChange(page - 1)}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>

                  <PageInfo theme={theme}>
                    Page {page}/{totalPages}
                  </PageInfo>

                  <Button
                    theme={theme}
                    onClick={() => handlePageChange(page + 1)}
                    disabled={page === totalPages}
                  >
                    Next
                  </Button>
                </PaginationContainer>
              )}
            </Sidebar>

            {/* Main content area with detail view */}
            <MainContent theme={theme}>
              {selectedItem ? (
                <>
                  {/* Format toggle button */}
                  <FormatToggleContainer theme={theme}>
                    <FormatToggleButton
                      theme={theme}
                      isActive={viewFormat === 'standard'}
                      onClick={() => {
                        console.log('Format toggle button clicked');
                        toggleViewFormat();
                      }}
                      title="Click to toggle between Standard and JSON view formats"
                    >
                      Format: {viewFormat === 'standard' ? 'Standard' : 'JSON'}
                    </FormatToggleButton>
                  </FormatToggleContainer>

                  {/* Detail view content */}
                  <DetailView theme={theme}>
                    {viewFormat === 'standard' ? (
                      renderStandardFormat()
                    ) : (
                      renderJsonFormat()
                    )}
                  </DetailView>

                  {/* Debug info */}
                  <div style={{
                    position: 'absolute',
                    bottom: '5px',
                    left: '5px',
                    fontSize: '10px',
                    color: '#999',
                    padding: '2px 5px',
                    backgroundColor: 'rgba(0,0,0,0.1)',
                    borderRadius: '3px'
                  }}>
                    View: {viewFormat}
                  </div>
                </>
              ) : (
                <StatusMessage theme={theme}>
                  Select a record to view details
                </StatusMessage>
              )}
            </MainContent>
          </MainContentContainer>
        )}
      </WidgetContent>
    </MongoDBViewerContainer>
  );
};

export default MongoDBViewerWidget;
