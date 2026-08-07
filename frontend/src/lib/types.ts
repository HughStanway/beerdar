export interface Address {
  street?: string;
  city?: string;
  postcode?: string;
}

export interface OpeningStatus {
  is_open_now?: boolean;
  raw?: string;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface Venue {
  id: string;
  name: string;
  type: string;
  distance_meters: number;
  walking_time_minutes: number;
  address?: Address;
  opening_status?: OpeningStatus;
  coordinates: Coordinates;
  maps_url: str;
}

export interface NearestResponse {
  status: string;
  query_location: Coordinates;
  primary_venue?: Venue;
  alternatives: Venue[];
}
