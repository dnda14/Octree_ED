using System.Collections.Generic;
using UnityEngine;

namespace Octrees
{
    public class Octree
    {
        public OctreeNode root;
        public Bounds bounds;

        public Octree(GameObject[] worldObjects, float minNodeSize)
        {
            CalculateBounds(worldObjects);
            createTree(worldObjects, minNodeSize);
        }

        void CalculateBounds(GameObject[] worldObjects)
        {
            foreach (var obj in worldObjects)
            {
             bounds.Encapsulate(obj.GetComponent<Collider>().bounds);   
            }
            Vector3 size = Vector3.one * Mathf.Max(bounds.size.x, bounds.size.y, bounds.size.z) * 0.5f;
            bounds.SetMinMax(bounds.center - size, bounds.center + size);
        }
        
        void createTree(GameObject[] worldObjects, float minNodeSize)
        {
            root = new OctreeNode(bounds, minNodeSize);

            foreach (var obj in worldObjects)
            {
                root.Divide(obj);
            }
        }

        public List<(OctreeObject, OctreeObject)> CheckCollisions()
        {
            return root.CheckCollisions();
        }
        
        
    }
}