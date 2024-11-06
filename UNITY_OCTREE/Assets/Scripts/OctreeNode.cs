using System.Collections.Generic;
using UnityEngine;

namespace Octrees
{
    public class OctreeNode
    {
        
        public Bounds bounds;
        static int nextId;
        public readonly int id;
        public List<OctreeObject> objetcs = new();
        public Bounds[] childBounds = new Bounds[8];
        public OctreeNode[] children;
        public bool IsLeaf => children == null;
        float minNodeSize;
        
        
        public OctreeNode(Bounds bounds, float minNodeSize)
        {
            this.bounds = bounds;
            this.minNodeSize = minNodeSize;
            id = nextId++;
            
            Vector3 newSize = bounds.size * 0.5f;
            Vector3 centerOffset = bounds.size * 0.25f;
            Vector3 parentCenter = bounds.center;

            for (int i = 0; i < 8; i++)
            {
                Vector3 childCenter = parentCenter;
                childCenter.x += centerOffset.x * ((i & 1) == 0 ? -1 : 1);
                childCenter.y += centerOffset.y * ((i & 2) == 0 ? -1 : 1);
                childCenter.z += centerOffset.z * ((i & 4) == 0 ? -1 : 1);
                childBounds[i] = new Bounds(childCenter, newSize);
            }
            
        }

        public void Divide(GameObject obj) => Divide(new OctreeObject(obj));

        private void Divide(OctreeObject octreeObject)
        {
            if (bounds.size.x <= minNodeSize)
            {
                AddObject(octreeObject);
                return;
            }

            children ??= new OctreeNode[8];
            
            bool intersectedChild = false;
            for (int i = 0; i < 8; i++)
            {
                children[i] ??= new OctreeNode(childBounds[i], minNodeSize);

                if (octreeObject.Intersects(childBounds[i]))
                {
                    children[i].Divide(octreeObject);
                    intersectedChild = true;
                }

                if (!intersectedChild)
                {
                    AddObject(octreeObject);
                }
            }
        }
        
        void AddObject(OctreeObject octreeObject) => objetcs.Add(octreeObject);

        public void drawNode ()
        {
            Gizmos.color = Color.green;
            Gizmos.DrawWireCube(bounds.center, bounds.size);

            foreach (OctreeObject obj in objetcs)
            {
                if (obj.Intersects(bounds))
                {
                    Gizmos.color = Color.red;
                    Gizmos.DrawWireCube(obj.bounds.center, obj.bounds.size);
                }
            }

            if (children != null)
            {
                foreach (OctreeNode child in children)
                {
                    if (child != null)
                    {
                        child.drawNode();
                    }
                }
            }
        }

        public List<(OctreeObject, OctreeObject)> CheckCollisions()
        {
            List<(OctreeObject, OctreeObject)> collisions = new();
            for (int i = 0; i < objetcs.Count; i++)
            {
                for (int j = i + 1; j < objetcs.Count; j++)
                {
                    if (objetcs[i].Intersects(objetcs[j].bounds))
                    {
                        collisions.Add((objetcs[i], objetcs[j]));   
                    }
                }
            }
            
            if (children != null)
            {
                foreach (OctreeNode child in children)
                {
                    if (child != null)
                    {
                        collisions.AddRange(child.CheckCollisions());
                    }
                }
            }
            
            return collisions;
        }

    }
}