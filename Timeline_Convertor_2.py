#!/usr/bin/env python3
"""
Timeline.json Converter
Converts Google Maps Timeline data to GeoJSON and KML/KMZ formats.

Supports:
- iOS Timeline.json (array format)
- Standard Timeline.json (timelineObjects format)
- Semantic Timeline.json (semanticSegments format)

Usage:
    Place this script in the same folder as Timeline.json and run it.
    Output files (Timeline.geojson, Timeline.kml, Timeline.kmz) will be 
    created in the same directory.
"""

import json
import os
import sys
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import xml.etree.ElementTree as ET
from xml.dom import minidom


def get_script_directory() -> Path:
    """Get the directory where this script is located."""
    # Use sys.argv[0] for better Windows compatibility
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(sys.argv[0]).resolve().parent


def parse_geo_string(geo_str: str) -> Optional[Tuple[float, float]]:
    """Parse 'geo:lat,lng' format strings."""
    if isinstance(geo_str, str) and geo_str.startswith('geo:'):
        parts = geo_str[4:].split(',')
        if len(parts) == 2:
            try:
                lat, lng = float(parts[0]), float(parts[1])
                return (lat, lng)
            except ValueError:
                pass
    return None


def parse_latlng_string(latlng_str: str) -> Optional[Tuple[float, float]]:
    """Parse '12.345°, 67.890°' format strings (semantic format)."""
    if not latlng_str:
        return None
    match = re.search(r'(-?\d+\.?\d*)\s*°?,?\s*(-?\d+\.?\d*)', latlng_str)
    if match:
        try:
            lat, lng = float(match.group(1)), float(match.group(2))
            return (lat, lng)
        except ValueError:
            pass
    return None


def get_activity_color(activity_type: str) -> str:
    """Return hex color for activity type."""
    colors = {
        'DRIVING': '#4285F4',
        'IN_VEHICLE': '#4285F4',
        'IN_PASSENGER_VEHICLE': '#4285F4',
        'DRIVE': '#4285F4',
        'IN_TAXI': '#FFEB3B',
        'MOTORCYCLING': '#1E90FF',
        'CYCLING': '#0F9D58',
        'ON_BICYCLE': '#0F9D58',
        'BICYCLE': '#0F9D58',
        'WALKING': '#DB4437',
        'ON_FOOT': '#DB4437',
        'WALK': '#DB4437',
        'RUNNING': '#DB4437',
        'HIKING': '#0F9D58',
        'IN_BUS': '#9C27B0',
        'IN_SUBWAY': '#673AB7',
        'IN_TRAIN': '#673AB7',
        'IN_TRAM': '#673AB7',
        'IN_FERRY': '#673AB7',
        'FLYING': '#03A9F4',
        'BOATING': '#00BCD4',
        'SWIMMING': '#00BCD4',
        'UNKNOWN': '#9E9E9E',
    }
    return colors.get(activity_type.upper(), '#9E9E9E')


def format_activity_type(activity_type: str) -> str:
    """Format activity type for display."""
    mappings = {
        'IN_VEHICLE': 'Driving',
        'IN_PASSENGER_VEHICLE': 'In Vehicle',
        'DRIVE': 'Driving',
        'IN_TAXI': 'Taxi',
        'MOTORCYCLING': 'Motorcycling',
        'ON_BICYCLE': 'Cycling',
        'CYCLING': 'Cycling',
        'BICYCLE': 'Cycling',
        'ON_FOOT': 'Walking',
        'WALKING': 'Walking',
        'WALK': 'Walking',
        'RUNNING': 'Running',
        'HIKING': 'Hiking',
        'IN_BUS': 'Bus',
        'IN_SUBWAY': 'Subway',
        'IN_TRAIN': 'Train',
        'IN_TRAM': 'Tram',
        'IN_FERRY': 'Ferry',
        'STILL': 'Stationary',
        'FLYING': 'Flying',
        'BOATING': 'Boating',
        'SWIMMING': 'Swimming',
    }
    return mappings.get(activity_type.upper(), activity_type.replace('_', ' ').title())


class TimelineConverter:
    """Converts Google Timeline data to various formats."""
    
    def __init__(self, input_path: Path):
        self.input_path = input_path
        self.data = None
        self.format_type = None  # 'ios', 'standard', or 'semantic'
        self.visits = []
        self.activities = []
        
    def load(self) -> bool:
        """Load and parse the Timeline.json file."""
        if not self.input_path.exists():
            print(f"Error: File not found: {self.input_path}")
            return False
            
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON file: {e}")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
            
        # Detect format and parse
        if isinstance(self.data, list):
            self.format_type = 'ios'
            self._parse_ios_format()
        elif 'timelineObjects' in self.data:
            self.format_type = 'standard'
            self._parse_standard_format()
        elif 'semanticSegments' in self.data:
            self.format_type = 'semantic'
            self._parse_semantic_format()
        else:
            print("Error: Unrecognized Timeline.json format")
            return False
            
        print(f"Loaded {len(self.visits)} visits and {len(self.activities)} activities")
        print(f"Format detected: {self.format_type}")
        return True
    
    def _parse_ios_format(self):
        """Parse iOS Timeline format (array of objects)."""
        for item in self.data:
            if not item or 'startTime' not in item or 'endTime' not in item:
                continue
                
            if 'visit' in item:
                visit = item['visit']
                candidate = visit.get('topCandidate', {})
                coords = parse_geo_string(candidate.get('placeLocation', ''))
                
                if coords:
                    self.visits.append({
                        'name': candidate.get('name', 'Unknown Location'),
                        'lat': coords[0],
                        'lng': coords[1],
                        'start_time': item['startTime'],
                        'end_time': item['endTime'],
                        'place_id': candidate.get('placeID'),
                        'semantic_type': candidate.get('semanticType'),
                    })
                    
            elif 'activity' in item:
                activity = item['activity']
                candidate = activity.get('topCandidate', {})
                start_coords = parse_geo_string(activity.get('start', ''))
                end_coords = parse_geo_string(activity.get('end', ''))
                
                path_points = []
                if start_coords:
                    path_points.append(start_coords)
                if end_coords and end_coords != start_coords:
                    path_points.append(end_coords)
                    
                if path_points:
                    self.activities.append({
                        'type': candidate.get('type', 'UNKNOWN'),
                        'start_time': item['startTime'],
                        'end_time': item['endTime'],
                        'distance': activity.get('distanceMeters', 0),
                        'path': path_points,
                    })
    
    def _parse_standard_format(self):
        """Parse standard Timeline format (timelineObjects)."""
        for item in self.data.get('timelineObjects', []):
            if 'placeVisit' in item:
                pv = item['placeVisit']
                loc = pv.get('location', {})
                duration = pv.get('duration', {})
                
                lat = loc.get('latitudeE7', 0) / 1e7
                lng = loc.get('longitudeE7', 0) / 1e7
                
                if lat and lng:
                    name = loc.get('name', 'Unknown Location')
                    semantic = loc.get('semanticType', '')
                    if semantic in ('TYPE_HOME', 'Home'):
                        name = 'Home'
                    elif semantic in ('TYPE_WORK', 'Work'):
                        name = 'Work'
                        
                    self.visits.append({
                        'name': name,
                        'lat': lat,
                        'lng': lng,
                        'start_time': duration.get('startTimestamp'),
                        'end_time': duration.get('endTimestamp'),
                        'place_id': loc.get('placeId'),
                        'semantic_type': semantic,
                    })
                    
            elif 'activitySegment' in item:
                seg = item['activitySegment']
                duration = seg.get('duration', {})
                
                path_points = []
                
                # Try different path sources
                path_data = (seg.get('waypointPath', {}).get('waypoints') or
                           seg.get('simplifiedRawPath', {}).get('points') or
                           seg.get('timelinePath', {}).get('points') or [])
                
                for pt in path_data:
                    lat = pt.get('latE7', 0) / 1e7 if 'latE7' in pt else pt.get('lat', 0)
                    lng = pt.get('lngE7', 0) / 1e7 if 'lngE7' in pt else pt.get('lng', 0)
                    if lat and lng:
                        path_points.append((lat, lng))
                
                # Fallback to start/end locations
                if len(path_points) < 2:
                    start_loc = seg.get('startLocation', {})
                    end_loc = seg.get('endLocation', {})
                    
                    start_lat = start_loc.get('latitudeE7', 0) / 1e7
                    start_lng = start_loc.get('longitudeE7', 0) / 1e7
                    end_lat = end_loc.get('latitudeE7', 0) / 1e7
                    end_lng = end_loc.get('longitudeE7', 0) / 1e7
                    
                    if start_lat and start_lng:
                        path_points = [(start_lat, start_lng)]
                    if end_lat and end_lng:
                        path_points.append((end_lat, end_lng))
                
                if path_points:
                    activity_type = (seg.get('activityType') or
                                   (seg.get('activities', [{}])[0].get('activityType') if seg.get('activities') else None) or
                                   'UNKNOWN')
                    
                    self.activities.append({
                        'type': activity_type,
                        'start_time': duration.get('startTimestamp'),
                        'end_time': duration.get('endTimestamp'),
                        'distance': seg.get('distance', 0),
                        'path': path_points,
                    })
    
    def _parse_semantic_format(self):
        """Parse semantic Timeline format (semanticSegments)."""
        for segment in self.data.get('semanticSegments', []):
            start_time = segment.get('startTime')
            end_time = segment.get('endTime')
            
            if 'visit' in segment:
                visit = segment['visit']
                candidate = visit.get('topCandidate', {})
                place_loc = candidate.get('placeLocation', {})
                coords = parse_latlng_string(place_loc.get('latLng', ''))
                
                if coords:
                    name = candidate.get('name', 'Unknown Location')
                    semantic = candidate.get('semanticType', '')
                    if semantic in ('TYPE_HOME', 'Home'):
                        name = 'Home'
                    elif semantic in ('TYPE_WORK', 'Work'):
                        name = 'Work'
                        
                    self.visits.append({
                        'name': name,
                        'lat': coords[0],
                        'lng': coords[1],
                        'start_time': start_time,
                        'end_time': end_time,
                        'place_id': candidate.get('placeId'),
                        'semantic_type': semantic,
                    })
                    
            elif 'activity' in segment:
                activity = segment['activity']
                candidate = activity.get('topCandidate', {})
                
                start_coords = parse_latlng_string(activity.get('start', {}).get('latLng', ''))
                end_coords = parse_latlng_string(activity.get('end', {}).get('latLng', ''))
                
                path_points = []
                
                # Get timeline path if available
                for pt in segment.get('timelinePath', []):
                    coords = parse_latlng_string(pt.get('point', ''))
                    if coords:
                        path_points.append(coords)
                
                # Fallback to start/end
                if len(path_points) < 2:
                    if start_coords:
                        path_points = [start_coords]
                    if end_coords:
                        path_points.append(end_coords)
                
                if path_points:
                    self.activities.append({
                        'type': candidate.get('type', 'UNKNOWN'),
                        'start_time': start_time,
                        'end_time': end_time,
                        'distance': activity.get('distanceMeters', 0),
                        'path': path_points,
                    })
    
    def to_geojson(self) -> dict:
        """Convert to GeoJSON format."""
        features = []
        
        # Add visits as Point features
        for visit in self.visits:
            # Extract date from start_time for filtering
            date_str = self._extract_date(visit['start_time'])
            
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [visit['lng'], visit['lat']]
                },
                'properties': {
                    'name': visit['name'],
                    'type': 'visit',
                    'date': date_str,
                    'year': self._extract_year(visit['start_time']),
                    'month': self._extract_month(visit['start_time']),
                    'day': self._extract_day(visit['start_time']),
                    'weekday': self._extract_weekday(visit['start_time']),
                    'start_time': visit['start_time'],
                    'end_time': visit['end_time'],
                    'place_id': visit.get('place_id'),
                    'semantic_type': visit.get('semantic_type'),
                    'marker-color': '#FF0000',
                    'marker-symbol': 'marker',
                }
            }
            features.append(feature)
        
        # Add activities as LineString features
        for activity in self.activities:
            # Extract date from start_time for filtering
            date_str = self._extract_date(activity['start_time'])
            
            if len(activity['path']) >= 2:
                coordinates = [[pt[1], pt[0]] for pt in activity['path']]  # GeoJSON is lng, lat
                geometry_type = 'LineString'
            else:
                # Single point - use Point geometry
                coordinates = [activity['path'][0][1], activity['path'][0][0]]
                geometry_type = 'Point'
            
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': geometry_type,
                    'coordinates': coordinates
                },
                'properties': {
                    'name': format_activity_type(activity['type']),
                    'type': 'activity',
                    'activity_type': activity['type'],
                    'date': date_str,
                    'year': self._extract_year(activity['start_time']),
                    'month': self._extract_month(activity['start_time']),
                    'day': self._extract_day(activity['start_time']),
                    'weekday': self._extract_weekday(activity['start_time']),
                    'start_time': activity['start_time'],
                    'end_time': activity['end_time'],
                    'distance_meters': activity['distance'],
                    'stroke': get_activity_color(activity['type']),
                    'stroke-width': 4,
                    'stroke-opacity': 0.8,
                }
            }
            features.append(feature)
        
        return {
            'type': 'FeatureCollection',
            'features': features
        }
    
    def _extract_date(self, timestamp: str) -> Optional[str]:
        """Extract YYYY-MM-DD date from timestamp."""
        if not timestamp:
            return None
        try:
            # Handle ISO format: 2024-01-15T10:30:00.000Z
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        except:
            try:
                # Try parsing just the date part
                return timestamp[:10] if len(timestamp) >= 10 else None
            except:
                return None
    
    def _extract_year(self, timestamp: str) -> Optional[int]:
        """Extract year from timestamp."""
        if not timestamp:
            return None
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.year
        except:
            try:
                return int(timestamp[:4])
            except:
                return None
    
    def _extract_month(self, timestamp: str) -> Optional[int]:
        """Extract month (1-12) from timestamp."""
        if not timestamp:
            return None
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.month
        except:
            try:
                return int(timestamp[5:7])
            except:
                return None
    
    def _extract_day(self, timestamp: str) -> Optional[int]:
        """Extract day of month from timestamp."""
        if not timestamp:
            return None
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.day
        except:
            try:
                return int(timestamp[8:10])
            except:
                return None
    
    def _extract_weekday(self, timestamp: str) -> Optional[str]:
        """Extract weekday name from timestamp."""
        if not timestamp:
            return None
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%A')  # Monday, Tuesday, etc.
        except:
            return None
    
    def to_kml(self) -> str:
        """Convert to KML format."""
        # Create KML structure
        kml = ET.Element('kml', xmlns='http://www.opengis.net/kml/2.2')
        document = ET.SubElement(kml, 'Document')
        
        # Add document name
        name = ET.SubElement(document, 'name')
        name.text = f'Timeline Export - {self.input_path.stem}'
        
        # Add styles for activities
        activity_types = set(a['type'] for a in self.activities)
        for act_type in activity_types:
            color = get_activity_color(act_type)
            # Convert hex to KML format (aabbggrr)
            hex_color = color.lstrip('#')
            kml_color = f'cc{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}'
            
            style = ET.SubElement(document, 'Style', id=act_type)
            line_style = ET.SubElement(style, 'LineStyle')
            ET.SubElement(line_style, 'color').text = kml_color
            ET.SubElement(line_style, 'width').text = '4'
        
        # Add style for visits
        visit_style = ET.SubElement(document, 'Style', id='visitStyle')
        icon_style = ET.SubElement(visit_style, 'IconStyle')
        ET.SubElement(icon_style, 'scale').text = '1.1'
        icon = ET.SubElement(icon_style, 'Icon')
        ET.SubElement(icon, 'href').text = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'
        
        # Group visits by date
        visits_by_date = {}
        for visit in self.visits:
            date_str = self._extract_date(visit['start_time']) or 'Unknown'
            if date_str not in visits_by_date:
                visits_by_date[date_str] = []
            visits_by_date[date_str].append(visit)
        
        # Group activities by date
        activities_by_date = {}
        for activity in self.activities:
            date_str = self._extract_date(activity['start_time']) or 'Unknown'
            if date_str not in activities_by_date:
                activities_by_date[date_str] = []
            activities_by_date[date_str].append(activity)
        
        # Get all unique dates and sort them
        all_dates = sorted(set(list(visits_by_date.keys()) + list(activities_by_date.keys())))
        
        # Create a folder for each date
        for date_str in all_dates:
            date_folder = ET.SubElement(document, 'Folder')
            ET.SubElement(date_folder, 'name').text = date_str
            
            # Add visits for this date
            date_visits = visits_by_date.get(date_str, [])
            if date_visits:
                visits_subfolder = ET.SubElement(date_folder, 'Folder')
                ET.SubElement(visits_subfolder, 'name').text = 'Places Visited'
                
                for visit in date_visits:
                    placemark = ET.SubElement(visits_subfolder, 'Placemark')
                    ET.SubElement(placemark, 'name').text = visit['name']
                    
                    desc_parts = [f"Date: {date_str}"]
                    if visit['start_time']:
                        desc_parts.append(f"Arrived: {visit['start_time']}")
                    if visit['end_time']:
                        desc_parts.append(f"Departed: {visit['end_time']}")
                    ET.SubElement(placemark, 'description').text = '\n'.join(desc_parts)
                    
                    # Add TimeSpan for time-based filtering in Google Earth
                    if visit['start_time'] and visit['end_time']:
                        timespan = ET.SubElement(placemark, 'TimeSpan')
                        ET.SubElement(timespan, 'begin').text = visit['start_time']
                        ET.SubElement(timespan, 'end').text = visit['end_time']
                    
                    ET.SubElement(placemark, 'styleUrl').text = '#visitStyle'
                    
                    point = ET.SubElement(placemark, 'Point')
                    ET.SubElement(point, 'coordinates').text = f"{visit['lng']},{visit['lat']},0"
            
            # Add activities for this date
            date_activities = activities_by_date.get(date_str, [])
            if date_activities:
                activities_subfolder = ET.SubElement(date_folder, 'Folder')
                ET.SubElement(activities_subfolder, 'name').text = 'Activities'
                
                for activity in date_activities:
                    if len(activity['path']) < 2:
                        continue
                        
                    placemark = ET.SubElement(activities_subfolder, 'Placemark')
                    ET.SubElement(placemark, 'name').text = format_activity_type(activity['type'])
                    
                    desc_parts = [f"Date: {date_str}"]
                    if activity['distance']:
                        dist_km = activity['distance'] / 1000
                        desc_parts.append(f"Distance: {dist_km:.1f} km")
                    if activity['start_time']:
                        desc_parts.append(f"Start: {activity['start_time']}")
                    if activity['end_time']:
                        desc_parts.append(f"End: {activity['end_time']}")
                    ET.SubElement(placemark, 'description').text = '\n'.join(desc_parts)
                    
                    # Add TimeSpan for time-based filtering in Google Earth
                    if activity['start_time'] and activity['end_time']:
                        timespan = ET.SubElement(placemark, 'TimeSpan')
                        ET.SubElement(timespan, 'begin').text = activity['start_time']
                        ET.SubElement(timespan, 'end').text = activity['end_time']
                    
                    ET.SubElement(placemark, 'styleUrl').text = f"#{activity['type']}"
                    
                    line_string = ET.SubElement(placemark, 'LineString')
                    ET.SubElement(line_string, 'tessellate').text = '1'
                    
                    coords = '\n'.join(f"{pt[1]},{pt[0]},0" for pt in activity['path'])
                    ET.SubElement(line_string, 'coordinates').text = coords
        
        # Pretty print
        xml_str = ET.tostring(kml, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')
    
    def save_geojson(self, output_path: Path) -> str:
        """Save as GeoJSON file."""
        geojson = self.to_geojson()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
            
        print(f"Saved GeoJSON: {output_path}")
        return str(output_path)
    
    def save_kml(self, output_path: Path) -> str:
        """Save as KML file."""
        kml = self.to_kml()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(kml)
            
        print(f"Saved KML: {output_path}")
        return str(output_path)
    
    def save_kmz(self, output_path: Path) -> str:
        """Save as KMZ file (compressed KML)."""
        kml = self.to_kml()
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('doc.kml', kml)
            
        print(f"Saved KMZ: {output_path}")
        return str(output_path)


def main():
    """Main entry point."""
    # Get the directory where this script is located
    script_dir = get_script_directory()
    
    # Look for Timeline.json in the same directory as the script
    input_file = script_dir / "Timeline.json"
    
    print(f"Looking for Timeline.json in: {script_dir}")
    print("-" * 50)
    
    if not input_file.exists():
        print(f"Error: Timeline.json not found!")
        print(f"Please place Timeline.json in the same folder as this script:")
        print(f"  {script_dir}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Create converter and load data
    converter = TimelineConverter(input_file)
    if not converter.load():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    if len(converter.visits) == 0 and len(converter.activities) == 0:
        print("Warning: No data found to convert!")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("-" * 50)
    print("Converting to all formats...")
    print("-" * 50)
    
    # Save all three formats in the same directory
    converter.save_geojson(script_dir / "Timeline.geojson")
    converter.save_kml(script_dir / "Timeline.kml")
    converter.save_kmz(script_dir / "Timeline.kmz")
    
    print("-" * 50)
    print("Conversion complete!")
    print(f"Output files saved to: {script_dir}")
    print("  - Timeline.geojson")
    print("  - Timeline.kml")
    print("  - Timeline.kmz")
    
    input("\nPress Enter to exit...")
    return 0


if __name__ == '__main__':
    sys.exit(main())
