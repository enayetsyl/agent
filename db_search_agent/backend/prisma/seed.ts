import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  console.log("🌱 Starting database seed...");

  // Check if data already exists (with error handling)
  let productCount = 0;
  let categoryCount = 0;

  try {
    productCount = await prisma.product.count();
    categoryCount = await prisma.category.count();
  } catch (error: any) {
    if (error.code === "P2021") {
      console.error("❌ Error: Database tables do not exist!");
      console.error("   Please run: npx prisma migrate deploy");
      console.error(
        "   Or restore from Phase 1: psql -U postgres -d ecommerce -f ../database/schema.sql"
      );
      process.exit(1);
    }
    throw error;
  }

  if (productCount > 0 || categoryCount > 0) {
    console.log(`⚠️  Database already contains data:`);
    console.log(`   - Products: ${productCount}`);
    console.log(`   - Categories: ${categoryCount}`);
    console.log(`\n💡 Skipping seed. Use --force flag to reset database.`);
    return;
  }

  console.log("📦 Seeding sample data...");

  // ============================================
  // Create Categories
  // ============================================
  console.log("Creating categories...");
  const categories = await Promise.all([
    prisma.category.create({
      data: {
        name: "Apparel",
        slug: "apparel",
        description: "Clothing and accessories",
      },
    }),
    prisma.category.create({
      data: {
        name: "Electronics",
        slug: "electronics",
        description: "Electronic devices and gadgets",
      },
    }),
    prisma.category.create({
      data: {
        name: "Footwear",
        slug: "footwear",
        description: "Shoes and boots",
      },
    }),
    prisma.category.create({
      data: {
        name: "Home & Garden",
        slug: "home-garden",
        description: "Home improvement and garden supplies",
      },
    }),
    prisma.category.create({
      data: {
        name: "Sports & Outdoors",
        slug: "sports-outdoors",
        description: "Sports equipment and outdoor gear",
      },
    }),
    prisma.category.create({
      data: {
        name: "Books & Media",
        slug: "books-media",
        description: "Books, movies, and music",
      },
    }),
  ]);

  const [
    apparel,
    electronics,
    footwear,
    homeGarden,
    sportsOutdoors,
    booksMedia,
  ] = categories;

  // ============================================
  // Create Products
  // ============================================
  console.log("Creating products...");
  const products = await Promise.all([
    prisma.product.create({
      data: {
        name: "Red Cotton T-Shirt",
        slug: "red-cotton-tshirt",
        description:
          "Comfortable 100% cotton t-shirt, perfect for everyday wear. Available in multiple sizes and colors. Machine washable.",
        shortDescription: "Comfortable cotton t-shirt",
        sku: "TSH-RED-001",
        price: 29.99,
        compareAtPrice: 39.99,
        categoryId: apparel.id,
        brand: "BasicWear",
        status: "active",
        featured: true,
      },
    }),
    prisma.product.create({
      data: {
        name: "Blue Denim Jeans",
        slug: "blue-denim-jeans",
        description:
          "Classic fit denim jeans with stretch comfort. Durable construction with reinforced seams. Perfect for casual wear.",
        shortDescription: "Classic fit jeans",
        sku: "JNS-BLU-001",
        price: 79.99,
        compareAtPrice: 99.99,
        categoryId: apparel.id,
        brand: "DenimCo",
        status: "active",
        featured: true,
      },
    }),
    prisma.product.create({
      data: {
        name: "Wireless Headphones",
        slug: "wireless-headphones",
        description:
          "Premium noise-cancelling wireless headphones with 30-hour battery life. Bluetooth 5.0 connectivity. Comfortable over-ear design.",
        shortDescription: "Noise-cancelling headphones",
        sku: "HD-WLS-001",
        price: 149.99,
        compareAtPrice: 199.99,
        categoryId: electronics.id,
        brand: "AudioTech",
        status: "active",
        featured: true,
      },
    }),
    prisma.product.create({
      data: {
        name: "Running Shoes",
        slug: "running-shoes",
        description:
          "Lightweight running shoes with cushioned sole and breathable mesh upper. Perfect for daily runs and workouts.",
        shortDescription: "Lightweight running shoes",
        sku: "SHO-RUN-001",
        price: 89.99,
        compareAtPrice: 119.99,
        categoryId: footwear.id,
        brand: "RunFast",
        status: "active",
        featured: true,
      },
    }),
    prisma.product.create({
      data: {
        name: "Garden Tool Set",
        slug: "garden-tool-set",
        description:
          "Complete 5-piece garden tool set including trowel, pruner, weeder, cultivator, and gloves. Durable stainless steel construction.",
        shortDescription: "5-piece garden tool set",
        sku: "GAR-SET-001",
        price: 49.99,
        categoryId: homeGarden.id,
        brand: "GardenPro",
        status: "active",
        featured: false,
      },
    }),
    prisma.product.create({
      data: {
        name: "Yoga Mat",
        slug: "yoga-mat",
        description:
          "Non-slip yoga mat with extra cushioning. Eco-friendly material. Includes carrying strap.",
        shortDescription: "Non-slip yoga mat",
        sku: "SPT-YOG-001",
        price: 34.99,
        compareAtPrice: 44.99,
        categoryId: sportsOutdoors.id,
        brand: "ZenFit",
        status: "active",
        featured: true,
      },
    }),
    prisma.product.create({
      data: {
        name: "Programming Book: TypeScript Guide",
        slug: "typescript-guide-book",
        description:
          "Comprehensive guide to TypeScript programming. Covers advanced topics and best practices. 500+ pages.",
        shortDescription: "TypeScript programming guide",
        sku: "BOK-TYP-001",
        price: 39.99,
        categoryId: booksMedia.id,
        brand: "TechBooks",
        status: "active",
        featured: false,
      },
    }),
    prisma.product.create({
      data: {
        name: "Black Leather Jacket",
        slug: "black-leather-jacket",
        description:
          "Classic black leather jacket with quilted lining. Genuine leather exterior. Available in sizes S-XL.",
        shortDescription: "Classic leather jacket",
        sku: "JKT-BLK-001",
        price: 199.99,
        compareAtPrice: 249.99,
        categoryId: apparel.id,
        brand: "LeatherCraft",
        status: "active",
        featured: true,
      },
    }),
    prisma.product.create({
      data: {
        name: "Smart Watch",
        slug: "smart-watch",
        description:
          "Feature-rich smartwatch with heart rate monitor, GPS, and 7-day battery life. Water-resistant up to 50m.",
        shortDescription: "Feature-rich smartwatch",
        sku: "WCH-SMT-001",
        price: 179.99,
        compareAtPrice: 229.99,
        categoryId: electronics.id,
        brand: "TechWear",
        status: "active",
        featured: true,
      },
    }),
    prisma.product.create({
      data: {
        name: "Hiking Boots",
        slug: "hiking-boots",
        description:
          "Waterproof hiking boots with ankle support. Vibram sole for excellent traction. Suitable for all terrains.",
        shortDescription: "Waterproof hiking boots",
        sku: "SHO-HIK-001",
        price: 129.99,
        compareAtPrice: 159.99,
        categoryId: footwear.id,
        brand: "TrailMaster",
        status: "active",
        featured: false,
      },
    }),
  ]);

  const [
    redTShirt,
    blueJeans,
    headphones,
    runningShoes,
    gardenTools,
    yogaMat,
    typescriptBook,
    leatherJacket,
    smartWatch,
    hikingBoots,
  ] = products;

  // ============================================
  // Create Product Variants
  // ============================================
  console.log("Creating product variants...");

  // Red Cotton T-Shirt variants
  const redTShirtVariants = await Promise.all([
    prisma.productVariant.create({
      data: {
        productId: redTShirt.id,
        name: "Size: S, Color: Red",
        sku: "TSH-RED-001-S-RED",
        price: 29.99,
        stockQuantity: 50,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: redTShirt.id,
        name: "Size: M, Color: Red",
        sku: "TSH-RED-001-M-RED",
        price: 29.99,
        stockQuantity: 75,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: redTShirt.id,
        name: "Size: L, Color: Red",
        sku: "TSH-RED-001-L-RED",
        price: 29.99,
        stockQuantity: 60,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: redTShirt.id,
        name: "Size: XL, Color: Red",
        sku: "TSH-RED-001-XL-RED",
        price: 29.99,
        stockQuantity: 40,
        trackInventory: true,
      },
    }),
  ]);

  // Blue Denim Jeans variants
  const blueJeansVariants = await Promise.all([
    prisma.productVariant.create({
      data: {
        productId: blueJeans.id,
        name: "Size: 30x32",
        sku: "JNS-BLU-001-30-32",
        price: 79.99,
        stockQuantity: 25,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: blueJeans.id,
        name: "Size: 32x32",
        sku: "JNS-BLU-001-32-32",
        price: 79.99,
        stockQuantity: 30,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: blueJeans.id,
        name: "Size: 34x32",
        sku: "JNS-BLU-001-34-32",
        price: 79.99,
        stockQuantity: 20,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: blueJeans.id,
        name: "Size: 36x32",
        sku: "JNS-BLU-001-36-32",
        price: 79.99,
        stockQuantity: 15,
        trackInventory: true,
      },
    }),
  ]);

  // Wireless Headphones (single variant)
  const headphonesVariant = await prisma.productVariant.create({
    data: {
      productId: headphones.id,
      name: "Standard",
      sku: "HD-WLS-001-STD",
      price: 149.99,
      stockQuantity: 100,
      trackInventory: true,
    },
  });

  // Running Shoes variants
  const runningShoesVariants = await Promise.all([
    prisma.productVariant.create({
      data: {
        productId: runningShoes.id,
        name: "Size: 8, Color: Black",
        sku: "SHO-RUN-001-8-BLK",
        price: 89.99,
        stockQuantity: 30,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: runningShoes.id,
        name: "Size: 9, Color: Black",
        sku: "SHO-RUN-001-9-BLK",
        price: 89.99,
        stockQuantity: 35,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: runningShoes.id,
        name: "Size: 10, Color: Black",
        sku: "SHO-RUN-001-10-BLK",
        price: 89.99,
        stockQuantity: 40,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: runningShoes.id,
        name: "Size: 11, Color: Black",
        sku: "SHO-RUN-001-11-BLK",
        price: 89.99,
        stockQuantity: 25,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: runningShoes.id,
        name: "Size: 9, Color: White",
        sku: "SHO-RUN-001-9-WHT",
        price: 89.99,
        stockQuantity: 20,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: runningShoes.id,
        name: "Size: 10, Color: White",
        sku: "SHO-RUN-001-10-WHT",
        price: 89.99,
        stockQuantity: 22,
        trackInventory: true,
      },
    }),
  ]);

  // Garden Tool Set (single variant)
  const gardenToolsVariant = await prisma.productVariant.create({
    data: {
      productId: gardenTools.id,
      name: "Standard Set",
      sku: "GAR-SET-001-STD",
      price: 49.99,
      stockQuantity: 50,
      trackInventory: true,
    },
  });

  // Yoga Mat (single variant)
  const yogaMatVariant = await prisma.productVariant.create({
    data: {
      productId: yogaMat.id,
      name: "Standard",
      sku: "SPT-YOG-001-STD",
      price: 34.99,
      stockQuantity: 80,
      trackInventory: true,
    },
  });

  // Programming Book (single variant)
  const typescriptBookVariant = await prisma.productVariant.create({
    data: {
      productId: typescriptBook.id,
      name: "Paperback",
      sku: "BOK-TYP-001-PBK",
      price: 39.99,
      stockQuantity: 15,
      trackInventory: true,
    },
  });

  // Black Leather Jacket variants
  const leatherJacketVariants = await Promise.all([
    prisma.productVariant.create({
      data: {
        productId: leatherJacket.id,
        name: "Size: S",
        sku: "JKT-BLK-001-S",
        price: 199.99,
        stockQuantity: 10,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: leatherJacket.id,
        name: "Size: M",
        sku: "JKT-BLK-001-M",
        price: 199.99,
        stockQuantity: 12,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: leatherJacket.id,
        name: "Size: L",
        sku: "JKT-BLK-001-L",
        price: 199.99,
        stockQuantity: 8,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: leatherJacket.id,
        name: "Size: XL",
        sku: "JKT-BLK-001-XL",
        price: 199.99,
        stockQuantity: 5,
        trackInventory: true,
      },
    }),
  ]);

  // Smart Watch (single variant)
  const smartWatchVariant = await prisma.productVariant.create({
    data: {
      productId: smartWatch.id,
      name: "Standard",
      sku: "WCH-SMT-001-STD",
      price: 179.99,
      stockQuantity: 60,
      trackInventory: true,
    },
  });

  // Hiking Boots variants
  const hikingBootsVariants = await Promise.all([
    prisma.productVariant.create({
      data: {
        productId: hikingBoots.id,
        name: "Size: 8",
        sku: "SHO-HIK-001-8",
        price: 129.99,
        stockQuantity: 18,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: hikingBoots.id,
        name: "Size: 9",
        sku: "SHO-HIK-001-9",
        price: 129.99,
        stockQuantity: 20,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: hikingBoots.id,
        name: "Size: 10",
        sku: "SHO-HIK-001-10",
        price: 129.99,
        stockQuantity: 22,
        trackInventory: true,
      },
    }),
    prisma.productVariant.create({
      data: {
        productId: hikingBoots.id,
        name: "Size: 11",
        sku: "SHO-HIK-001-11",
        price: 129.99,
        stockQuantity: 15,
        trackInventory: true,
      },
    }),
  ]);

  // ============================================
  // Create Variant Attributes
  // ============================================
  console.log("Creating variant attributes...");

  // Red Cotton T-Shirt attributes
  await Promise.all([
    prisma.variantAttribute.create({
      data: {
        variantId: redTShirtVariants[0].id,
        attributeName: "size",
        attributeValue: "S",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: redTShirtVariants[0].id,
        attributeName: "color",
        attributeValue: "Red",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: redTShirtVariants[1].id,
        attributeName: "size",
        attributeValue: "M",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: redTShirtVariants[1].id,
        attributeName: "color",
        attributeValue: "Red",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: redTShirtVariants[2].id,
        attributeName: "size",
        attributeValue: "L",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: redTShirtVariants[2].id,
        attributeName: "color",
        attributeValue: "Red",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: redTShirtVariants[3].id,
        attributeName: "size",
        attributeValue: "XL",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: redTShirtVariants[3].id,
        attributeName: "color",
        attributeValue: "Red",
      },
    }),
  ]);

  // Blue Denim Jeans attributes
  await Promise.all([
    prisma.variantAttribute.create({
      data: {
        variantId: blueJeansVariants[0].id,
        attributeName: "waist",
        attributeValue: "30",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: blueJeansVariants[0].id,
        attributeName: "inseam",
        attributeValue: "32",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: blueJeansVariants[1].id,
        attributeName: "waist",
        attributeValue: "32",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: blueJeansVariants[1].id,
        attributeName: "inseam",
        attributeValue: "32",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: blueJeansVariants[2].id,
        attributeName: "waist",
        attributeValue: "34",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: blueJeansVariants[2].id,
        attributeName: "inseam",
        attributeValue: "32",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: blueJeansVariants[3].id,
        attributeName: "waist",
        attributeValue: "36",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: blueJeansVariants[3].id,
        attributeName: "inseam",
        attributeValue: "32",
      },
    }),
  ]);

  // Running Shoes attributes
  await Promise.all([
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[0].id,
        attributeName: "size",
        attributeValue: "8",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[0].id,
        attributeName: "color",
        attributeValue: "Black",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[1].id,
        attributeName: "size",
        attributeValue: "9",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[1].id,
        attributeName: "color",
        attributeValue: "Black",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[2].id,
        attributeName: "size",
        attributeValue: "10",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[2].id,
        attributeName: "color",
        attributeValue: "Black",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[3].id,
        attributeName: "size",
        attributeValue: "11",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[3].id,
        attributeName: "color",
        attributeValue: "Black",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[4].id,
        attributeName: "size",
        attributeValue: "9",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[4].id,
        attributeName: "color",
        attributeValue: "White",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[5].id,
        attributeName: "size",
        attributeValue: "10",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: runningShoesVariants[5].id,
        attributeName: "color",
        attributeValue: "White",
      },
    }),
  ]);

  // Black Leather Jacket attributes
  await Promise.all([
    prisma.variantAttribute.create({
      data: {
        variantId: leatherJacketVariants[0].id,
        attributeName: "size",
        attributeValue: "S",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: leatherJacketVariants[1].id,
        attributeName: "size",
        attributeValue: "M",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: leatherJacketVariants[2].id,
        attributeName: "size",
        attributeValue: "L",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: leatherJacketVariants[3].id,
        attributeName: "size",
        attributeValue: "XL",
      },
    }),
  ]);

  // Hiking Boots attributes
  await Promise.all([
    prisma.variantAttribute.create({
      data: {
        variantId: hikingBootsVariants[0].id,
        attributeName: "size",
        attributeValue: "8",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: hikingBootsVariants[1].id,
        attributeName: "size",
        attributeValue: "9",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: hikingBootsVariants[2].id,
        attributeName: "size",
        attributeValue: "10",
      },
    }),
    prisma.variantAttribute.create({
      data: {
        variantId: hikingBootsVariants[3].id,
        attributeName: "size",
        attributeValue: "11",
      },
    }),
  ]);

  // ============================================
  // Create Product Images
  // ============================================
  console.log("Creating product images...");
  await Promise.all([
    prisma.productImage.create({
      data: {
        productId: redTShirt.id,
        url: "https://via.placeholder.com/800x800?text=Red+Cotton+T-Shirt",
        altText: "Red Cotton T-Shirt",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
    prisma.productImage.create({
      data: {
        productId: blueJeans.id,
        url: "https://via.placeholder.com/800x800?text=Blue+Denim+Jeans",
        altText: "Blue Denim Jeans",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
    prisma.productImage.create({
      data: {
        productId: headphones.id,
        url: "https://via.placeholder.com/800x800?text=Wireless+Headphones",
        altText: "Wireless Headphones",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
    prisma.productImage.create({
      data: {
        productId: runningShoes.id,
        url: "https://via.placeholder.com/800x800?text=Running+Shoes",
        altText: "Running Shoes",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
    prisma.productImage.create({
      data: {
        productId: gardenTools.id,
        url: "https://via.placeholder.com/800x800?text=Garden+Tool+Set",
        altText: "Garden Tool Set",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
    prisma.productImage.create({
      data: {
        productId: yogaMat.id,
        url: "https://via.placeholder.com/800x800?text=Yoga+Mat",
        altText: "Yoga Mat",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
    prisma.productImage.create({
      data: {
        productId: typescriptBook.id,
        url: "https://via.placeholder.com/800x800?text=TypeScript+Guide+Book",
        altText: "TypeScript Guide Book",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
    prisma.productImage.create({
      data: {
        productId: leatherJacket.id,
        url: "https://via.placeholder.com/800x800?text=Black+Leather+Jacket",
        altText: "Black Leather Jacket",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
    prisma.productImage.create({
      data: {
        productId: smartWatch.id,
        url: "https://via.placeholder.com/800x800?text=Smart+Watch",
        altText: "Smart Watch",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
    prisma.productImage.create({
      data: {
        productId: hikingBoots.id,
        url: "https://via.placeholder.com/800x800?text=Hiking+Boots",
        altText: "Hiking Boots",
        sortOrder: 1,
        isPrimary: true,
      },
    }),
  ]);

  // ============================================
  // Create Product Tags
  // ============================================
  console.log("Creating product tags...");
  const tags = await Promise.all([
    prisma.productTag.create({
      data: { name: "New Arrival", slug: "new-arrival" },
    }),
    prisma.productTag.create({
      data: { name: "Best Seller", slug: "best-seller" },
    }),
    prisma.productTag.create({ data: { name: "Sale", slug: "sale" } }),
    prisma.productTag.create({
      data: { name: "Eco-Friendly", slug: "eco-friendly" },
    }),
    prisma.productTag.create({ data: { name: "Premium", slug: "premium" } }),
    prisma.productTag.create({ data: { name: "Casual", slug: "casual" } }),
    prisma.productTag.create({
      data: { name: "Sportswear", slug: "sportswear" },
    }),
    prisma.productTag.create({
      data: { name: "Accessories", slug: "accessories" },
    }),
  ]);

  const [
    newArrival,
    bestSeller,
    sale,
    ecoFriendly,
    premium,
    casual,
    sportswear,
    accessories,
  ] = tags;

  // ============================================
  // Create Product Tag Relations
  // ============================================
  console.log("Creating product tag relations...");
  await Promise.all([
    prisma.productTagRelation.create({
      data: { productId: redTShirt.id, tagId: newArrival.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: redTShirt.id, tagId: casual.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: blueJeans.id, tagId: bestSeller.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: blueJeans.id, tagId: casual.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: headphones.id, tagId: bestSeller.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: headphones.id, tagId: premium.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: runningShoes.id, tagId: sportswear.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: yogaMat.id, tagId: ecoFriendly.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: yogaMat.id, tagId: sportswear.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: leatherJacket.id, tagId: premium.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: smartWatch.id, tagId: newArrival.id },
    }),
    prisma.productTagRelation.create({
      data: { productId: smartWatch.id, tagId: premium.id },
    }),
  ]);

  // ============================================
  // Create Product Reviews
  // ============================================
  console.log("Creating product reviews...");
  await Promise.all([
    prisma.productReview.create({
      data: {
        productId: redTShirt.id,
        userId: 1,
        rating: 5,
        title: "Great quality!",
        reviewText: "Love this t-shirt. Very comfortable and fits perfectly.",
        verifiedPurchase: true,
        helpfulCount: 12,
      },
    }),
    prisma.productReview.create({
      data: {
        productId: redTShirt.id,
        userId: 2,
        rating: 4,
        title: "Good value",
        reviewText: "Nice shirt for the price. Material is soft.",
        verifiedPurchase: true,
        helpfulCount: 8,
      },
    }),
    prisma.productReview.create({
      data: {
        productId: blueJeans.id,
        userId: 1,
        rating: 5,
        title: "Perfect fit",
        reviewText:
          "These jeans fit great and are very comfortable. Highly recommend!",
        verifiedPurchase: true,
        helpfulCount: 15,
      },
    }),
    prisma.productReview.create({
      data: {
        productId: headphones.id,
        userId: 3,
        rating: 5,
        title: "Excellent sound quality",
        reviewText:
          "Best headphones I have ever owned. Battery life is amazing!",
        verifiedPurchase: true,
        helpfulCount: 23,
      },
    }),
    prisma.productReview.create({
      data: {
        productId: headphones.id,
        userId: 4,
        rating: 4,
        title: "Good but could be better",
        reviewText:
          "Sound is great but the ear cups could be more comfortable.",
        verifiedPurchase: true,
        helpfulCount: 5,
      },
    }),
    prisma.productReview.create({
      data: {
        productId: runningShoes.id,
        userId: 2,
        rating: 5,
        title: "Great running shoes",
        reviewText: "Lightweight and comfortable. Perfect for my daily runs.",
        verifiedPurchase: true,
        helpfulCount: 18,
      },
    }),
    prisma.productReview.create({
      data: {
        productId: yogaMat.id,
        userId: 5,
        rating: 5,
        title: "Perfect yoga mat",
        reviewText:
          "Non-slip surface works great. Very happy with this purchase.",
        verifiedPurchase: true,
        helpfulCount: 10,
      },
    }),
    prisma.productReview.create({
      data: {
        productId: smartWatch.id,
        userId: 3,
        rating: 4,
        title: "Feature-rich watch",
        reviewText: "Lots of features and good battery life. GPS is accurate.",
        verifiedPurchase: true,
        helpfulCount: 14,
      },
    }),
  ]);

  console.log("✅ Seed completed successfully!");
  console.log(`   - ${categories.length} categories`);
  console.log(`   - ${products.length} products`);
  console.log(`   - ${tags.length} tags`);
  console.log(`   - 8 product reviews`);
}

main()
  .catch((e) => {
    console.error("❌ Error seeding database:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
