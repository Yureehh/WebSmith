export type LeadProfile = {
  status: string;
  opportunity_summary: string | null;
  mission_summary: string | null;
  review_sentiment_summary: string | null;
  pain_points_json: string[];
  recommended_angle: string | null;
  market_type: "b2c" | "b2b" | "both" | "unknown";
  audience_notes: string | null;
  next_follow_up_at: string | null;
  do_not_contact_reason: string | null;
  notes: string | null;
};

export type SourceDocument = {
  id: number;
  source_type: string;
  source_url: string | null;
  title: string | null;
  content_text: string | null;
  extracted_json: Record<string, unknown>;
  confidence: string | null;
  created_at: string;
};

export type Contact = {
  id: number;
  name: string | null;
  role: string | null;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  profile_url: string | null;
  source_url: string | null;
  contact_type: string;
  confidence: string;
  allowed_for_manual_contact: boolean;
  do_not_contact: boolean;
  created_at: string;
};

export type WebsiteProject = {
  id: number;
  business_id: number;
  status: string;
  generation_mode: string;
  project_name: string;
  repo_path: string | null;
  preview_url: string | null;
  brief_markdown: string | null;
  generated_copy_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type Business = {
  id: number;
  created_at: string;
  updated_at: string;
  name: string;
  formatted_address: string | null;
  lat: number | null;
  lng: number | null;
  website_url: string | null;
  phone: string | null;
  email: string | null;
  primary_category: string | null;
  categories_json: string[];
  discovery_source: string;
  lead_profile: LeadProfile | null;
  contacts: Contact[];
  source_documents: SourceDocument[];
  website_projects: WebsiteProject[];
};

export type CoverageTile = {
  id: string;
  label: string;
  lat: number;
  lng: number;
  radius_km: number;
  status: "pending" | "success" | "empty" | "error";
  result_count: number;
  error: string | null;
};

export type SearchRun = {
  id: number;
  location_query: string;
  center_lat: number | null;
  center_lng: number | null;
  radius_km: number;
  categories_json: string[];
  keywords: string | null;
  max_results: number;
  search_depth: "fast" | "balanced" | "deep";
  provider_order_json: string[];
  coverage_json: CoverageTile[];
  provider_errors_json: Record<string, unknown>[];
  total_seen_count: number;
  new_added_count: number;
  duplicate_skipped_count: number;
  excluded_count: number;
  status: string;
  error_message: string | null;
};

export type ProviderSettings = {
  discovery_provider: string;
  overpass_configured: boolean;
  web_search_backup_enabled: boolean;
  enrich_web_search_enabled: boolean;
  ai_key_configured: boolean;
};

export type JobResult = {
  id: number;
  type: string;
  status: "queued" | "running" | "succeeded" | "failed";
  payload_json: Record<string, unknown>;
  result_json: Record<string, unknown> | null;
  error: string | null;
};
