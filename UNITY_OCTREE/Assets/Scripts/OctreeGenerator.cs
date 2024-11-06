using System;
using UnityEngine;

namespace Octrees
{
    public class OctreeGenerator : MonoBehaviour
    {
        public GameObject[] objects;
        public float minNodeSize = 1f;
        Octree octree;
        
        void Awake() => octree = new Octree(objects, minNodeSize);

        private void Update()
        {
            octree = new Octree(objects, minNodeSize);
            
            var collisions = octree.CheckCollisions();
            foreach (var collision in collisions)
            {
                Debug.Log($"Collision detected between {collision.Item1.bounds} and {collision.Item2.bounds}");
            }
        }

        void OnDrawGizmos()
        {
            Gizmos.color = Color.green;
            Gizmos.DrawWireCube(octree.bounds.center, octree.bounds.size);
            octree.root.drawNode();
            
        }
    }
}