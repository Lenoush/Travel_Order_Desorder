// types.ts

// Interface pour une réponse de route
export interface RouteResponse {
    IDsentence: number;
    responsesmodel: RouteItem[] | string[];
    text: string;
    itinerary: ItineraryItem[];
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
