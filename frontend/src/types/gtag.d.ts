/** Google Analytics gtag type definitions */

declare global {
    interface Window {
        dataLayer: unknown[];
        gtag?: Gtag.Gtag;
    }
}

/** GA4 gtag function type */
declare namespace Gtag {
    type Gtag = (
        command: 'config' | 'event' | 'js' | 'set' | 'consent',
        targetIdOrEventName: string | Date,
        config?: ControlParams | EventParams | CustomParams
    ) => void;

    interface ControlParams {
        groups?: string | string[];
        send_to?: string | string[];
        event_callback?: () => void;
        event_timeout?: number;
    }

    interface EventParams {
        page_title?: string;
        page_location?: string;
        page_path?: string;
        [key: string]: string | number | boolean | undefined | (() => void);
    }

    interface CustomParams {
        [key: string]: string | number | boolean | undefined | (() => void);
    }
}

export {};
