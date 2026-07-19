import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const galleryItem = (image: any) =>
  z.object({
    image: image(),
    alt: z.string().default(""),
    caption: z.string().optional(),
    // still: normal tile | wide: drag-to-pan flat image | 360: full sphere view
    view: z.enum(["still", "wide", "360"]).default("still"),
  });

const settings = defineCollection({
  loader: glob({ pattern: "settings.yml", base: "./content" }),
  schema: ({ image }) =>
    z.object({
      site_title: z.string(),
      theme: z.enum(["classic", "studio", "exhibit"]).default("classic"),
      palette: z.enum(["gallery", "verdant", "coral", "indigo"]).default("gallery"),
      default_mode: z.enum(["light", "dark"]).default("light"),
      hero: z.object({
        heading: z.string(),
        subheading: z.string(),
        image: image(),
        image_alt: z.string().default(""),
      }),
      footer: z.object({
        email: z.string(),
        linkedin: z.string().url(),
      }),
    }),
});

const about = defineCollection({
  loader: glob({ pattern: "about.md", base: "./content" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      order: z.number(),
      headshot: image(),
      headshot_alt: z.string().default(""),
      badges: z
        .array(z.object({ image: image(), alt: z.string().default("") }))
        .default([]),
    }),
});

const galleries = defineCollection({
  // Folder collection: Jolene can create whole new gallery sections in the CMS.
  loader: glob({ pattern: "*.yml", base: "./content/galleries" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      order: z.number(),
      layout: z.enum(["masonry", "rows", "mosaic", "squares"]).default("masonry"),
      notes: z.array(z.string()).default([]),
      gallery: z.array(galleryItem(image)),
    }),
});

const conceptual = defineCollection({
  loader: glob({ pattern: "*.md", base: "./content/conceptual" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      label: z.string(),
      order: z.number(),
      brief: z.string(),
      layout: z.enum(["masonry", "rows", "mosaic", "squares"]).default("masonry"),
      gallery: z.array(galleryItem(image)),
    }),
});

const textiles = defineCollection({
  loader: glob({ pattern: "*.yml", base: "./content/textiles" }),
  schema: ({ image }) =>
    z.object({
      name: z.string(),
      inspiration: z.string(),
      order: z.number(),
      swatches: z.array(
        z.object({
          image: image(),
          colorway: z.string(),
        })
      ),
    }),
});

const resume = defineCollection({
  loader: glob({ pattern: "resume.yml", base: "./content" }),
  schema: z.object({
    title: z.string(),
    order: z.number(),
    pdf: z.string(),
    email: z.string(),
  }),
});

export const collections = { settings, about, galleries, conceptual, textiles, resume };
