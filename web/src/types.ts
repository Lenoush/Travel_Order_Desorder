// types.ts

// Interface pour une réponse de route
export interface RouteResponse {
    IDsentence: number;
    responsesmodel: RouteItem[];
    text: string;
    itinerary: ItineraryItem[];
    error_nlp: string[];
    error_route: string[];
}
  
// Interface pour un élément de route
export interface RouteItem {
    label: string;
    word: string;
}

export interface ItineraryItem {
    Itineraire: string;
    Duree_totale: string;
    Correspondance: string[];
}
