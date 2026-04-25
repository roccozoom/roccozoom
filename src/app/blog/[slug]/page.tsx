import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { PrismaClient } from "@prisma/client";
import { Metadata } from "next";

const prisma = new PrismaClient({
  datasourceUrl: process.env.DATABASE_URL || "file:./dev.db"
});

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const blog = await prisma.blogPost.findUnique({ where: { slug } });
  if (!blog) return { title: "Play Guide Not Found | RoccoZoom" };
  
  return {
    title: `${blog.title} | RoccoZoom Play Guides`,
    description: blog.metaDescription || blog.summary,
    openGraph: {
      title: blog.title,
      description: blog.metaDescription || blog.summary,
      images: [blog.imageUrl],
    }
  };
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const blog = await prisma.blogPost.findUnique({
    where: { slug }
  });

  if (!blog) notFound();

  return (
    <div className="bg-white">
      {/* Hero */}
      <div className="relative h-[50vh] min-h-[400px] w-full bg-zinc-950 flex items-center justify-center">
        <Image src={blog.imageUrl} alt={blog.title} fill className="object-cover opacity-50" priority />
        <div className="relative z-10 max-w-4xl mx-auto px-6 text-center text-white">
          <span className="inline-block py-1.5 px-4 rounded-full bg-blue-500/20 text-blue-300 text-[10px] font-bold tracking-widest uppercase mb-6 backdrop-blur-md">
            Parenting Guide
          </span>
          <h1 className="font-playfair text-4xl md:text-6xl font-bold leading-tight mb-6">
            {blog.title}
          </h1>
          <p className="text-zinc-300 text-lg md:text-xl max-w-2xl mx-auto">
            {blog.summary}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-3xl mx-auto px-6 py-16 md:py-24">
        <Link href="/blog" className="text-xs font-bold tracking-widest uppercase text-zinc-400 hover:text-blue-500 transition-colors mb-12 block">
          ← Back to all posts
        </Link>
        
        {/* We use prose to style HTML content safely */}
        <article className="prose prose-zinc prose-lg md:prose-xl prose-headings:font-playfair prose-headings:font-bold prose-a:text-blue-500 hover:prose-a:text-blue-600 prose-img:rounded-3xl max-w-none prose-p:leading-relaxed">
          <div dangerouslySetInnerHTML={{ __html: blog.content }} />
        </article>

        <div className="mt-24 pt-12 border-t border-zinc-100">
          <div className="bg-blue-50 rounded-3xl p-10 text-center">
            <h3 className="font-playfair text-2xl font-bold text-zinc-900 mb-4">Loved this guide?</h3>
            <p className="text-zinc-600 mb-8 max-w-md mx-auto">Subscribe to our newsletter to get the latest play guides and Amazon toy drops every week.</p>
            <Link href="/#newsletter" className="inline-block bg-blue-500 hover:bg-blue-600 text-white text-xs font-bold tracking-widest uppercase py-4 px-8 rounded-full transition-colors shadow-xl shadow-blue-500/20">
              Subscribe Free
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
