CREATE TABLE "print_jobs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sku" varchar(50) NOT NULL,
	"product_name" varchar(255) NOT NULL,
	"lot_number" varchar(20) NOT NULL,
	"quantity" integer NOT NULL,
	"status" varchar(20) NOT NULL,
	"error_message" text,
	"printer_name" varchar(100),
	"printed_at" timestamp with time zone DEFAULT now(),
	"printed_by" varchar(100)
);
--> statement-breakpoint
CREATE TABLE "products" (
	"id" serial PRIMARY KEY NOT NULL,
	"sku" varchar(50) NOT NULL,
	"product_name" varchar(255) NOT NULL,
	"grade_or_concentration" varchar(100),
	"product_family" varchar(50),
	"package_type" varchar(50) NOT NULL,
	"net_contents_us" varchar(50) NOT NULL,
	"net_contents_metric" varchar(50) NOT NULL,
	"cas_number" varchar(20),
	"upc_gtin12" varchar(12) NOT NULL,
	"hazcom_applicable" boolean DEFAULT false,
	"ghs_pictograms" text[],
	"signal_word" varchar(20),
	"hazard_statements" text[],
	"precaution_statements" text[],
	"dot_regulated" boolean DEFAULT false,
	"un_number" varchar(10),
	"proper_shipping_name" varchar(255),
	"hazard_class" varchar(10),
	"packing_group" varchar(5),
	"nfpa_health" smallint,
	"nfpa_fire" smallint,
	"nfpa_reactivity" smallint,
	"nfpa_special" varchar(10),
	"sds_url" text,
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now(),
	CONSTRAINT "products_sku_unique" UNIQUE("sku"),
	CONSTRAINT "products_upc_gtin12_unique" UNIQUE("upc_gtin12")
);
--> statement-breakpoint
CREATE INDEX "idx_print_jobs_date" ON "print_jobs" USING btree ("printed_at");--> statement-breakpoint
CREATE INDEX "idx_print_jobs_sku" ON "print_jobs" USING btree ("sku");--> statement-breakpoint
CREATE INDEX "idx_products_upc" ON "products" USING btree ("upc_gtin12");--> statement-breakpoint
CREATE INDEX "idx_products_sku" ON "products" USING btree ("sku");