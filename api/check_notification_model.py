"""Check if notifications table exists and if Prisma recognizes it"""
import asyncio
from prisma import Prisma

async def check_notifications():
    prisma = Prisma()
    await prisma.connect()
    
    print("✅ Connected to database\n")
    
    # Check if notifications table exists
    tables = await prisma.query_raw('SELECT tablename FROM pg_tables WHERE schemaname=\'public\' ORDER BY tablename')
    table_names = [t['tablename'] for t in tables]
    
    print(f"📊 Database tables ({len(table_names)}):")
    for table in table_names:
        marker = "✅" if table == "notifications" else "  "
        print(f"  {marker} {table}")
    
    print(f"\n🔍 Checking Prisma client attributes...")
    prisma_attrs = [attr for attr in dir(prisma) if not attr.startswith('_') and attr.islower()]
    print(f"   Total models: {len(prisma_attrs)}")
    
    if 'notification' in prisma_attrs:
        print(f"   ✅ prisma.notification EXISTS")
    else:
        print(f"   ❌ prisma.notification NOT FOUND")
        print(f"   Available models: {prisma_attrs}")
    
    # Try to count notifications
    print(f"\n🧪 Testing prisma.notification...")
    try:
        count = await prisma.notification.count()
        print(f"   ✅ prisma.notification.count() = {count}")
    except AttributeError as e:
        print(f"   ❌ Error: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    await prisma.disconnect()
    print(f"\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(check_notifications())
