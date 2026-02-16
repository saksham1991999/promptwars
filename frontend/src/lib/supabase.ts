/** Supabase client initialization */
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabasePublishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabasePublishableKey) {
    throw new Error(
        'Supabase configuration missing. Please set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY environment variables.'
    );
}

export const supabase = createClient(supabaseUrl, supabasePublishableKey, {
    realtime: {
        params: {
            eventsPerSecond: 10, // Throttle events to prevent overwhelming the client
        },
    },
});
