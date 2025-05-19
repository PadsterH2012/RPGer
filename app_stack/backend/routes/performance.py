"""
Performance monitoring API routes.
"""

import os
import logging
import psutil
import time
from flask import Blueprint, jsonify, request

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
performance_bp = Blueprint('performance', __name__)

# Cache for performance data to avoid frequent calculations
performance_cache = {
    'last_update': 0,
    'data': None,
    'interval': 5  # Cache for 5 seconds
}

@performance_bp.route('/', methods=['GET'])
def get_performance():
    """Get system performance metrics."""
    try:
        # Check if we have cached data that's still fresh
        current_time = time.time()
        if performance_cache['data'] and (current_time - performance_cache['last_update'] < performance_cache['interval']):
            return jsonify(performance_cache['data'])
        
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Get memory usage
        memory = psutil.virtual_memory()
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        
        # Get network stats
        net_io = psutil.net_io_counters()
        
        # Get process info
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent(interval=0.1)
        process_threads = process.num_threads()
        
        # Build response
        performance_data = {
            'system': {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': {
                        'current': cpu_freq.current if cpu_freq else None,
                        'min': cpu_freq.min if cpu_freq else None,
                        'max': cpu_freq.max if cpu_freq else None
                    }
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            },
            'process': {
                'pid': process.pid,
                'cpu_percent': process_cpu,
                'memory': {
                    'rss': process_memory.rss,  # Resident Set Size
                    'vms': process_memory.vms,  # Virtual Memory Size
                    'shared': getattr(process_memory, 'shared', 0)  # Shared memory
                },
                'threads': process_threads,
                'create_time': process.create_time()
            },
            'timestamp': current_time
        }
        
        # Update cache
        performance_cache['data'] = performance_data
        performance_cache['last_update'] = current_time
        
        return jsonify(performance_data)
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({
            'error': 'Failed to get performance metrics',
            'message': str(e)
        }), 500
