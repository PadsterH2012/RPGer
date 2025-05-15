/**
 * Widget Registry Service
 * 
 * Manages the registration and retrieval of widgets in the application.
 */

import { 
  WidgetRegistration, 
  WidgetMetadata, 
  WidgetComponent,
  WidgetCategory,
  WidgetEventType,
  WidgetEvent,
  WidgetEventHandler,
  WidgetConfig
} from '../types/widget';

class WidgetRegistry {
  private widgets: Map<string, WidgetRegistration> = new Map();
  private eventHandlers: Map<string, Set<WidgetEventHandler>> = new Map();
  
  /**
   * Register a widget with the registry
   * 
   * @param registration Widget registration information
   * @returns boolean indicating success
   */
  public registerWidget(registration: WidgetRegistration): boolean {
    if (this.widgets.has(registration.metadata.id)) {
      console.warn(`Widget with ID ${registration.metadata.id} is already registered.`);
      return false;
    }
    
    this.widgets.set(registration.metadata.id, registration);
    
    // Emit widget registered event
    this.emitEvent({
      type: WidgetEventType.INIT,
      widgetId: registration.metadata.id
    });
    
    return true;
  }
  
  /**
   * Unregister a widget from the registry
   * 
   * @param widgetId Widget ID to unregister
   * @returns boolean indicating success
   */
  public unregisterWidget(widgetId: string): boolean {
    if (!this.widgets.has(widgetId)) {
      console.warn(`Widget with ID ${widgetId} is not registered.`);
      return false;
    }
    
    // Emit widget unregistered event
    this.emitEvent({
      type: WidgetEventType.DESTROY,
      widgetId
    });
    
    return this.widgets.delete(widgetId);
  }
  
  /**
   * Get a widget by ID
   * 
   * @param widgetId Widget ID
   * @returns Widget registration or undefined if not found
   */
  public getWidget(widgetId: string): WidgetRegistration | undefined {
    return this.widgets.get(widgetId);
  }
  
  /**
   * Get all registered widgets
   * 
   * @returns Array of widget registrations
   */
  public getAllWidgets(): WidgetRegistration[] {
    return Array.from(this.widgets.values());
  }
  
  /**
   * Get widgets by category
   * 
   * @param category Widget category
   * @returns Array of widget registrations in the specified category
   */
  public getWidgetsByCategory(category: WidgetCategory): WidgetRegistration[] {
    return this.getAllWidgets().filter(
      widget => widget.metadata.category === category
    );
  }
  
  /**
   * Update widget configuration
   * 
   * @param widgetId Widget ID
   * @param config New configuration
   * @returns boolean indicating success
   */
  public updateWidgetConfig(widgetId: string, config: WidgetConfig): boolean {
    const widget = this.widgets.get(widgetId);
    
    if (!widget) {
      console.warn(`Widget with ID ${widgetId} is not registered.`);
      return false;
    }
    
    // Emit config change event
    this.emitEvent({
      type: WidgetEventType.CONFIG_CHANGE,
      widgetId,
      payload: config
    });
    
    return true;
  }
  
  /**
   * Register an event handler
   * 
   * @param eventType Event type to listen for
   * @param handler Event handler function
   */
  public addEventListener(eventType: WidgetEventType, handler: WidgetEventHandler): void {
    const eventKey = eventType.toString();
    
    if (!this.eventHandlers.has(eventKey)) {
      this.eventHandlers.set(eventKey, new Set());
    }
    
    this.eventHandlers.get(eventKey)?.add(handler);
  }
  
  /**
   * Remove an event handler
   * 
   * @param eventType Event type
   * @param handler Event handler function to remove
   * @returns boolean indicating success
   */
  public removeEventListener(eventType: WidgetEventType, handler: WidgetEventHandler): boolean {
    const eventKey = eventType.toString();
    const handlers = this.eventHandlers.get(eventKey);
    
    if (!handlers) {
      return false;
    }
    
    return handlers.delete(handler);
  }
  
  /**
   * Emit a widget event
   * 
   * @param event Widget event to emit
   */
  public emitEvent(event: WidgetEvent): void {
    const eventKey = event.type.toString();
    const handlers = this.eventHandlers.get(eventKey);
    
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(event);
        } catch (error) {
          console.error(`Error in widget event handler for ${event.type}:`, error);
        }
      });
    }
  }
}

// Create singleton instance
const widgetRegistry = new WidgetRegistry();

export default widgetRegistry;
