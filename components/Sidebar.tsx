import { h, FunctionComponent } from "preact";
import { pagesPath } from "./config.ts";

async function getPages(folder: string): Promise<string[]> {
  const files = [];
  for await (const dirEntry of Deno.readDir(folder)) {
    if (dirEntry.isFile) {
      files.push(dirEntry.name);
    }
  }
  return files;
}


interface SidebarProps {
  pages: getPages(pagesPath);
  activeItem: string | null;
}

export const Sidebar: FunctionComponent<SidebarProps> = ({ pages, activeItem }) => {
  const handleClick = (item: string) => {
    // Handle click event
  };

  return (
    <div className="sidebar">
      {pages.map((item: string) => (
        <p
          key={item}
          onClick={() => handleClick(item)}
          class={item === activeItem ? "nav-item active" : "nav-item"}
        >
          {item}
        </p>
      ))}
    </div>
  );
};