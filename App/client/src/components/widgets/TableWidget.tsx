/**
 * TableWidget Component
 * 
 * Widget for displaying tabular data.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTheme } from '../../context/ThemeContext';
import { useSocket } from '../../context/SocketContext';
import { WidgetProps, WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';

const TableContainer = styled.div`
  height: 100%;
  overflow: auto;
`;

const StyledTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
`;

const TableHeader = styled.thead`
  background-color: var(--${props => props.theme}-surface-variant);
  position: sticky;
  top: 0;
  z-index: 1;
`;

const TableHeaderCell = styled.th`
  padding: var(--spacing-sm);
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid var(--${props => props.theme}-border);
  cursor: pointer;
  
  &:hover {
    background-color: var(--${props => props.theme}-hover);
  }
`;

const TableBody = styled.tbody``;

const TableRow = styled.tr<{ isEven: boolean }>`
  background-color: ${props => props.isEven 
    ? props.theme === 'dark' ? 'rgba(255, 255, 255, 0.03)' : 'rgba(0, 0, 0, 0.02)'
    : 'transparent'};
  
  &:hover {
    background-color: var(--${props => props.theme}-hover);
  }
`;

const TableCell = styled.td`
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--${props => props.theme}-border);
`;

const EmptyState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--${props => props.theme}-text-secondary);
  font-style: italic;
`;

const SearchContainer = styled.div`
  margin-bottom: var(--spacing-sm);
  display: flex;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: var(--spacing-sm);
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-sm);
  background-color: var(--${props => props.theme}-surface);
  color: var(--${props => props.theme}-text-primary);
  
  &:focus {
    outline: none;
    border-color: var(--${props => props.theme}-primary);
  }
`;

const PaginationContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-sm);
`;

const PageInfo = styled.div`
  color: var(--${props => props.theme}-text-secondary);
`;

const PaginationButton = styled.button<{ disabled?: boolean }>`
  background-color: ${props => props.disabled 
    ? props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'
    : `var(--${props.theme}-primary)`};
  color: ${props => props.disabled 
    ? `var(--${props.theme}-text-disabled)`
    : props.theme === 'dark' ? 'black' : 'white'};
  border: none;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.disabled ? 0.5 : 1};
  
  &:not(:disabled):hover {
    background-color: var(--${props => props.theme}-primary-variant);
  }
`;

interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
}

interface TableWidgetConfig {
  columns: TableColumn[];
  pageSize: number;
  showSearch: boolean;
  showPagination: boolean;
  dataSource?: string;
}

const defaultConfig: TableWidgetConfig = {
  columns: [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'value', label: 'Value', sortable: true },
  ],
  pageSize: 10,
  showSearch: true,
  showPagination: true,
  dataSource: 'default',
};

interface TableData {
  [key: string]: any;
}

const TableWidget: React.FC<WidgetProps> = ({ id, config }) => {
  const { theme } = useTheme();
  const { socket, isConnected } = useSocket();
  const widgetConfig = { ...defaultConfig, ...config } as TableWidgetConfig;
  
  const [data, setData] = useState<TableData[]>([]);
  const [filteredData, setFilteredData] = useState<TableData[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
  
  // Request data from server when connected
  useEffect(() => {
    if (socket && isConnected) {
      socket.emit('widget:requestData', {
        widgetId: id,
        dataSource: widgetConfig.dataSource,
      });
      
      // Listen for data updates
      const handleDataUpdate = (response: { widgetId: string; data: TableData[] }) => {
        if (response.widgetId === id) {
          setData(response.data);
        }
      };
      
      socket.on('widget:tableData', handleDataUpdate);
      
      return () => {
        socket.off('widget:tableData', handleDataUpdate);
      };
    } else {
      // Use sample data when not connected
      setData([
        { id: 1, name: 'Item 1', value: 100 },
        { id: 2, name: 'Item 2', value: 200 },
        { id: 3, name: 'Item 3', value: 300 },
        { id: 4, name: 'Item 4', value: 400 },
        { id: 5, name: 'Item 5', value: 500 },
      ]);
    }
  }, [socket, isConnected, id, widgetConfig.dataSource]);
  
  // Filter and sort data
  useEffect(() => {
    let result = [...data];
    
    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(item => 
        Object.values(item).some(
          value => value && value.toString().toLowerCase().includes(term)
        )
      );
    }
    
    // Apply sorting
    if (sortConfig) {
      result.sort((a, b) => {
        const aValue = a[sortConfig.key];
        const bValue = b[sortConfig.key];
        
        if (aValue < bValue) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }
    
    setFilteredData(result);
    setCurrentPage(1); // Reset to first page when filter changes
  }, [data, searchTerm, sortConfig]);
  
  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };
  
  // Handle column header click for sorting
  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'asc';
    
    if (sortConfig && sortConfig.key === key) {
      direction = sortConfig.direction === 'asc' ? 'desc' : 'asc';
    }
    
    setSortConfig({ key, direction });
  };
  
  // Calculate pagination
  const totalPages = Math.ceil(filteredData.length / widgetConfig.pageSize);
  const startIndex = (currentPage - 1) * widgetConfig.pageSize;
  const endIndex = Math.min(startIndex + widgetConfig.pageSize, filteredData.length);
  const currentData = filteredData.slice(startIndex, endIndex);
  
  // Handle pagination
  const goToPage = (page: number) => {
    setCurrentPage(page);
  };
  
  return (
    <TableContainer>
      {widgetConfig.showSearch && (
        <SearchContainer>
          <SearchInput
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={handleSearchChange}
            theme={theme}
          />
        </SearchContainer>
      )}
      
      <StyledTable>
        <TableHeader theme={theme}>
          <tr>
            {widgetConfig.columns.map(column => (
              <TableHeaderCell
                key={column.key}
                onClick={() => column.sortable && handleSort(column.key)}
                theme={theme}
                style={{ cursor: column.sortable ? 'pointer' : 'default' }}
              >
                {column.label}
                {sortConfig && sortConfig.key === column.key && (
                  <span>{sortConfig.direction === 'asc' ? ' ▲' : ' ▼'}</span>
                )}
              </TableHeaderCell>
            ))}
          </tr>
        </TableHeader>
        <TableBody>
          {currentData.length > 0 ? (
            currentData.map((row, index) => (
              <TableRow key={row.id || index} isEven={index % 2 === 0} theme={theme}>
                {widgetConfig.columns.map(column => (
                  <TableCell key={column.key} theme={theme}>
                    {row[column.key]}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <tr>
              <td colSpan={widgetConfig.columns.length}>
                <EmptyState theme={theme}>
                  No data available
                </EmptyState>
              </td>
            </tr>
          )}
        </TableBody>
      </StyledTable>
      
      {widgetConfig.showPagination && filteredData.length > 0 && (
        <PaginationContainer>
          <PaginationButton
            onClick={() => goToPage(currentPage - 1)}
            disabled={currentPage === 1}
            theme={theme}
          >
            Previous
          </PaginationButton>
          
          <PageInfo theme={theme}>
            Page {currentPage} of {totalPages} ({startIndex + 1}-{endIndex} of {filteredData.length})
          </PageInfo>
          
          <PaginationButton
            onClick={() => goToPage(currentPage + 1)}
            disabled={currentPage === totalPages}
            theme={theme}
          >
            Next
          </PaginationButton>
        </PaginationContainer>
      )}
    </TableContainer>
  );
};

export default withWidget(TableWidget, {
  metadata: {
    name: 'Table',
    description: 'Display data in a tabular format',
    category: WidgetCategory.UTILITY,
    icon: '📊',
    defaultSize: {
      w: 8,
      h: 4,
    },
    minW: 4,
    minH: 2,
  },
  defaultConfig,
});
