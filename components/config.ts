import { join } from "https://deno.land/std@0.221.0/path/mod.ts";

export const pagesPath: string = join(Deno.cwd(), "routes", "pages")